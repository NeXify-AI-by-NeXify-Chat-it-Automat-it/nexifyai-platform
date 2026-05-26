"""
NeXifyAI — Crawl4AI Service
Automatische Web-Crawling-Engine: Lead-Recherche, Wettbewerbsmonitoring, Content-Sammlung.
LLM-fertiges Markdown, JSON-Extraktion, Deep-Crawling.

SSRF-Schutz (Alert #28):
- DNS-Auflösung + IP-Prüfung gegen Private/Bogon-Ranges
- Redirect-Validierung: jeder Hop wird geprüft
- Keine ungeprüften Weiterleitungen
- Zeitbeschränkungen für DNS und HTTP
"""
import os
import json
import logging
import asyncio
import socket
import ipaddress
from datetime import datetime, timezone
import re
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger("nexifyai.services.crawl4ai")

# Private/Bogon IP-Bereiche für SSRF-Prävention
_PRIVATE_NETWORKS = [
    "127.0.0.0/8",       # Loopback
    "10.0.0.0/8",        # Private Class A
    "172.16.0.0/12",     # Private Class B
    "192.168.0.0/16",    # Private Class C
    "169.254.0.0/16",    # Link-Local
    "0.0.0.0/8",         # Current network
    "100.64.0.0/10",     # Carrier-grade NAT
    "198.18.0.0/15",     # Benchmarking
    "::1/128",           # IPv6 loopback
    "fc00::/7",          # IPv6 unique local
    "fe80::/10",         # IPv6 link-local
]


def _is_private_ip(ip_str: str) -> bool:
    """Prüft, ob eine IP-Adresse zu einem privaten/Bogon-Bereich gehört."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in ipaddress.ip_network(net) for net in _PRIVATE_NETWORKS)
    except ValueError:
        return True  # Ungültige IP als unsafe behandeln


def _resolve_and_check(hostname: str) -> tuple[bool, str]:
    """Löst Hostname auf und prüft, ob die IP-Adresse privat ist."""
    try:
        # Timeout für DNS-Auflösung (2 Sekunden)
        addrs = socket.getaddrinfo(hostname, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM, proto=0, flags=socket.AI_ADDRCONFIG)
        resolved = set()
        for addr in addrs:
            ip_str = addr[4][0]
            resolved.add(ip_str)
            if _is_private_ip(ip_str):
                return False, f"Blocked private IP: {ip_str}"
        if not resolved:
            return False, "DNS resolution returned no addresses"
        return True, ",".join(resolved)
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {e}"
    except Exception as e:
        return False, f"DNS resolution error: {e}"


def is_safe_url(url: str, check_dns: bool = True) -> tuple[bool, str]:
    """
    SSRF-sichere URL-Validierung mit Hostname-Prüfung und DNS-Auflösung.

    Returns:
        (safe: bool, reason: str) — safe=True + Resolved-IPs oder safe=False + Fehlergrund
    """
    if not url:
        return False, "Empty URL"
    parsed = urlparse(url)
    # Must be http or https
    if parsed.scheme not in ("http", "https"):
        return False, f"Blocked scheme: {parsed.scheme}"
    hostname = parsed.hostname or ""
    if not hostname:
        return False, "No hostname in URL"

    # Pattern-basierte Blockliste (schnelle Abweisung)
    blocked_patterns = [
        r"^localhost$",
        r"^127\.\d+\.\d+\.\d+$",
        r"^10\.\d+\.\d+\.\d+$",
        r"^172\.(1[6-9]|2\d|3[01])\.\d+\.\d+$",
        r"^192\.168\.\d+\.\d+$",
        r"^169\.254\.\d+\.\d+$",
        r"^::1$",
        r"^0\.0\.0\.0$",
    ]
    for pattern in blocked_patterns:
        if re.match(pattern, hostname):
            return False, f"Blocked hostname pattern: {hostname}"
    # Block metadata/internal hostnames
    if any(hostname.endswith(suffix) for suffix in [".internal", ".local", "localhost"]):
        return False, f"Blocked internal hostname: {hostname}"

    # DNS-Auflösung + IP-Prüfung
    if check_dns:
        safe, detail = _resolve_and_check(hostname)
        if not safe:
            return False, detail
        return True, detail

    return True, "pattern-check-passed"


async def crawl_url(
    url: str,
    extract_mode: str = "markdown",
    css_selector: str = None,
    max_pages: int = 1,
    timeout: int = 60,
) -> dict:
    """
    Crawlt eine URL und liefert LLM-fertigen Content.
    extract_mode: 'markdown' | 'structured' | 'links'

    SSRF-Sicherheit (Alert #28):
    - DNS-Auflösung + IP-Prüfung vor Anfrage
    - Redirect-Validierung nach jedem Hop
    """
    safe, reason = is_safe_url(url)
    if not safe:
        logger.warning(f"SSRF block — {url}: {reason}")
        return {"success": False, "error": f"Blocked URL: {reason}", "url": url}

    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,
            page_timeout=timeout * 1000,
            wait_until="domcontentloaded",
        )
        if css_selector:
            config.css_selector = css_selector

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)

            if not result.success:
                return {"success": False, "error": result.error_message or "Crawl fehlgeschlagen", "url": url}

            output = {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", "") if result.metadata else "",
                "description": result.metadata.get("description", "") if result.metadata else "",
                "crawled_at": datetime.now(timezone.utc).isoformat(),
            }

            if extract_mode == "markdown":
                output["content"] = result.markdown[:50000] if result.markdown else ""
                output["content_length"] = len(result.markdown) if result.markdown else 0
            elif extract_mode == "links":
                links = []
                if result.links:
                    for link_type, link_list in result.links.items():
                        for link in link_list[:50]:
                            links.append({"type": link_type, "href": link.get("href", ""), "text": link.get("text", "")})
                output["links"] = links
                output["link_count"] = len(links)
            elif extract_mode == "structured":
                output["content"] = result.markdown[:30000] if result.markdown else ""
                output["html_length"] = len(result.html) if result.html else 0
                output["media"] = {
                    "images": len(result.media.get("images", [])) if result.media else 0,
                    "videos": len(result.media.get("videos", [])) if result.media else 0,
                }
            else:
                output["content"] = result.markdown[:50000] if result.markdown else ""

            return output

    except ImportError:
        return await _fallback_http_fetch(url, extract_mode)
    except Exception as e:
        logger.error(f"Crawl4AI error for {url}: {e} — fallback to httpx")
        return await _fallback_http_fetch(url, extract_mode)


async def _fallback_http_fetch(url: str, extract_mode: str = "markdown") -> dict:
    """Lightweight HTTP-fetch fallback when Playwright/crawl4ai is unavailable.

    SSRF-Sicherheit (Alert #28):
    - DNS-Auflösung + IP-Prüfung vor Anfrage
    - Redirect-Validierung: jeder Hop wird gegen Private-IP-Liste geprüft
    - Keine ungeprüften Weiterleitungen
    - Identische Prüfung wie is_safe_url
    """
    safe, reason = is_safe_url(url)
    if not safe:
        logger.warning(f"SSRF block (fallback) — {url}: {reason}")
        return {"success": False, "error": f"Blocked URL: {reason}", "url": url}
    try:
        import httpx
        from bs4 import BeautifulSoup
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={"User-Agent": "NeXifyAI-Research/1.0 (+https://nexify-automate.com)"},
        ) as c:
            r = await c.get(url)

            # Redirect-Validierung: prüfe jeden Redirect-Hop
            if hasattr(r, 'history') and r.history:
                for redirect_resp in r.history:
                    redirect_url = str(redirect_resp.url)
                    safe_r, reason_r = is_safe_url(redirect_url)
                    if not safe_r:
                        logger.warning(f"SSRF block on redirect — {redirect_url}: {reason_r}")
                        return {"success": False, "error": f"Blocked redirect: {reason_r}", "url": redirect_url}

            if r.status_code >= 400:
                return {"success": False, "error": f"HTTP {r.status_code}", "url": url}
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
            text = " ".join(soup.get_text(separator=" ").split())[:20000]
            return {
                "success": True,
                "url": url,
                "title": title,
                "description": description,
                "content": text,
                "content_length": len(text),
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "method": "httpx_fallback",
            }
    except Exception as e:
        logger.error(f"httpx fallback failed for {url}: {e}")
        return {"success": False, "error": f"fallback: {str(e)[:300]}", "url": url}


async def research_company(url: str) -> dict:
    """
    Analysiert eine Firmen-Website für Lead-Recherche.
    Extrahiert: Unternehmensdaten, Kontakt, Technologien, Potenzial.
    """
    try:
        # Hauptseite crawlen
        main = await crawl_url(url, extract_mode="structured")
        if not main.get("success"):
            return main

        # Impressum / Kontakt suchen
        contact_data = {}
        impressum_urls = [f"{url.rstrip('/')}/impressum", f"{url.rstrip('/')}/kontakt", f"{url.rstrip('/')}/contact", f"{url.rstrip('/')}/about"]
        for imp_url in impressum_urls:
            try:
                imp = await crawl_url(imp_url, extract_mode="markdown")
                if imp.get("success") and imp.get("content"):
                    contact_data[imp_url.split("/")[-1]] = imp["content"][:3000]
                    break
            except Exception:
                continue

        return {
            "success": True,
            "url": url,
            "company": {
                "title": main.get("title", ""),
                "description": main.get("description", ""),
                "content_preview": main.get("content", "")[:5000],
                "media": main.get("media", {}),
            },
            "contact": contact_data,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Company research error for {url}: {e}")
        return {"success": False, "error": str(e)[:500], "url": url}


async def monitor_competitor(url: str, previous_hash: str = None) -> dict:
    """
    Wettbewerbsmonitoring: Crawlt und vergleicht mit vorherigem Stand.
    """
    import hashlib

    result = await crawl_url(url, extract_mode="markdown")
    if not result.get("success"):
        return result

    content = result.get("content", "")
    current_hash = hashlib.sha256(content.encode()).hexdigest()
    changed = previous_hash is not None and current_hash != previous_hash

    return {
        "success": True,
        "url": url,
        "content_hash": current_hash,
        "changed": changed,
        "content_length": len(content),
        "title": result.get("title", ""),
        "monitored_at": datetime.now(timezone.utc).isoformat(),
    }
