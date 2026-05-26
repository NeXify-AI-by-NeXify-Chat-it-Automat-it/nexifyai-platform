"""
NeXifyAI — Crawl4AI Service
Automatische Web-Crawling-Engine: Lead-Recherche, Wettbewerbsmonitoring, Content-Sammlung.
LLM-fertiges Markdown, JSON-Extraktion, Deep-Crawling.
"""
import os
import json
import logging
import asyncio
import ipaddress
import socket
from datetime import datetime, timezone
import re
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger("nexifyai.services.crawl4ai")

# Max redirects to follow (prevents open-redirect SSRF loops)
MAX_REDIRECTS = 5

# RFC 1918, RFC 4193, RFC 4291 private/internal IP ranges
PRIVATE_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),      # RFC 6598 (CGNAT)
    ipaddress.ip_network("127.0.0.0/8"),          # Loopback
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local
    ipaddress.ip_network("172.16.0.0/12"),        # RFC 1918
    ipaddress.ip_network("192.0.0.0/24"),         # RFC 5736
    ipaddress.ip_network("192.0.2.0/24"),         # Documentation (TEST-NET-1)
    ipaddress.ip_network("192.168.0.0/16"),       # RFC 1918
    ipaddress.ip_network("198.18.0.0/15"),        # RFC 2544 (benchmarking)
    ipaddress.ip_network("198.51.100.0/24"),      # Documentation (TEST-NET-2)
    ipaddress.ip_network("203.0.113.0/24"),       # Documentation (TEST-NET-3)
    ipaddress.ip_network("240.0.0.0/4"),          # Reserved
    ipaddress.ip_network("::1/128"),              # IPv6 loopback
    ipaddress.ip_network("::/96"),                # IPv4-compatible IPv6
    ipaddress.ip_network("::ffff:0:0/96"),        # IPv4-mapped IPv6
    ipaddress.ip_network("64:ff9b::/96"),         # RFC 6052
    ipaddress.ip_network("100::/64"),             # RFC 6666
    ipaddress.ip_network("2001:db8::/32"),        # Documentation
    ipaddress.ip_network("fc00::/7"),             # Unique local (RFC 4193)
    ipaddress.ip_network("fe80::/10"),            # Link-local (RFC 4291)
    ipaddress.ip_network("ff00::/8"),             # Multicast
]


def _is_private_ip(host: str) -> bool:
    """Check if a hostname resolves to a private/internal IP address."""
    try:
        addr = ipaddress.ip_address(host)
        return any(addr in net for net in PRIVATE_NETWORKS)
    except ValueError:
        pass
    return False


def _resolve_and_check(hostname: str) -> bool:
    """Resolve a hostname to IP addresses and check if any are private."""
    try:
        addrinfo = socket.getaddrinfo(hostname, None)
        for info in addrinfo:
            ip_str = info[4][0]
            try:
                addr = ipaddress.ip_address(ip_str)
                if any(addr in net for net in PRIVATE_NETWORKS):
                    return True
            except ValueError:
                continue
    except (socket.gaierror, OSError):
        # Resolution failure — block to be safe (could be internal hostname)
        return True
    return False


def _normalize_host(host: str) -> str:
    """Normalize obfuscated IP representations. Handles hex, octal, decimal dword."""
    # Strip IPv6 zone IDs (e.g., fe80::1%eth0)
    host = host.split("%")[0]

    # Check octal dotted FIRST: 0177.0.0.1 (must precede dotted decimal check)
    if re.match(r"^0[0-7]+\.\d+\.\d+\.\d+$", host):
        parts = host.split(".")
        try:
            decoded = []
            for p in parts:
                if p.startswith("0") and len(p) > 1 and all(c in "01234567" for c in p.strip()):
                    decoded.append(str(int(p, 8)))
                else:
                    decoded.append(p)
            return ".".join(decoded)
        except (ValueError, TypeError):
            pass

    # Check if it's a standard dotted decimal already
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", host):
        return host

    # Try to parse as decimal integer (dword IP: 2130706433 = 127.0.0.1)
    try:
        dword = int(host)
        if 0 <= dword <= 0xFFFFFFFF:
            return str(ipaddress.IPv4Address(dword))
    except (ValueError, TypeError):
        pass

    # Try to parse as hex (0x7f000001, 7f000001)
    hex_stripped = host.lower().lstrip("0x")
    if re.match(r"^[0-9a-f]{6,8}$", hex_stripped):
        try:
            return str(ipaddress.IPv4Address(int(hex_stripped, 16)))
        except (ValueError, TypeError):
            pass

    # Try octal dotted: 0177.0.0.1
    if re.match(r"^0[0-7]+\.\d+\.\d+\.\d+$", host):
        parts = host.split(".")
        try:
            decoded_parts = []
            for p in parts:
                if p.startswith("0") and len(p) > 1 and all(c in "01234567" for c in p.lstrip("0") or "0"):
                    decoded_parts.append(str(int(p, 8)))
                else:
                    decoded_parts.append(p)
            return ".".join(decoded_parts)
        except (ValueError, TypeError):
            pass

    return host


def _strip_url_credentials(url: str) -> str:
    """Strip embedded credentials from a URL (SSRF risk via auth info)."""
    parsed = urlparse(url)
    if parsed.username or parsed.password:
        clean = f"{parsed.scheme}://{parsed.hostname}"
        if parsed.port:
            clean += f":{parsed.port}"
        clean += parsed.path
        if parsed.query:
            clean += f"?{parsed.query}"
        if parsed.fragment:
            clean += f"#{parsed.fragment}"
        return clean
    return url


def is_safe_url(url: str, check_resolved: bool = True) -> bool:
    """Validate URL to prevent SSRF attacks.

    Args:
        url: URL to validate
        check_resolved: If True, also resolves hostname to check IPs.
                        Use False in sync contexts; async callers should use is_safe_url_async.

    Returns:
        True if URL is safe to fetch, False if blocked
    """
    if not url:
        logger.warning("SSRF check: empty URL blocked")
        return False

    # Strip credentials first
    url = _strip_url_credentials(url)

    parsed = urlparse(url)

    # Must be http or https
    if parsed.scheme not in ("http", "https"):
        logger.warning(f"SSRF check: non-http(s) scheme blocked: {parsed.scheme}")
        return False

    hostname = parsed.hostname or ""
    if not hostname:
        logger.warning("SSRF check: URL with no hostname blocked")
        return False

    # Normalize host (handle obfuscated IP formats)
    normalized = _normalize_host(hostname)

    # Check for private IPs directly
    if _is_private_ip(normalized):
        logger.warning(f"SSRF check: private IP blocked: {normalized} (from {hostname})")
        return False

    # Block internal/meta hostnames
    blocked_suffixes = [".internal", ".local", ".localhost", ".lan"]
    for suffix in blocked_suffixes:
        if normalized.endswith(suffix):
            logger.warning(f"SSRF check: internal hostname blocked: {normalized}")
            return False

    # DNS resolution check (block hostnames resolving to private IPs)
    if check_resolved and _resolve_and_check(normalized):
        logger.warning(f"SSRF check: hostname resolves to private IP: {normalized}")
        return False

    return True


async def is_safe_url_async(url: str) -> bool:
    """Async SSRF URL validation with DNS resolution.

    Use this in async contexts instead of is_safe_url(url, check_resolved=True)
    to avoid blocking the event loop during DNS resolution.
    """
    if not url:
        return False
    url = _strip_url_credentials(url)
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = parsed.hostname or ""
    if not hostname:
        return False
    normalized = _normalize_host(hostname)
    if _is_private_ip(normalized):
        return False
    for suffix in [".internal", ".local", ".localhost", ".lan"]:
        if normalized.endswith(suffix):
            return False

    # DNS resolution (async via event loop to avoid blocking)
    try:
        addrinfo = await asyncio.get_event_loop().getaddrinfo(normalized, None)
        for info in addrinfo:
            ip_str = info[4][0]
            try:
                addr = ipaddress.ip_address(ip_str)
                if any(addr in net for net in PRIVATE_NETWORKS):
                    return False
            except ValueError:
                continue
    except (socket.gaierror, OSError):
        return False

    return True


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
    """
    # Async SSRF check with DNS resolution
    if not await is_safe_url_async(url):
        logger.warning(f"SSRF blocked: {url}")
        return {"success": False, "error": "Invalid or blocked URL (SSRF prevention)", "url": url}

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

            # Check if the final URL after redirects is safe
            final_url = getattr(result, "url", url) or url
            if final_url != url and not await is_safe_url_async(final_url):
                logger.warning(f"SSRF blocked (redirect target): {final_url}")
                return {"success": False, "error": "Redirect target blocked (SSRF prevention)", "url": url, "blocked_redirect": final_url}

            output = {
                "success": True,
                "url": final_url,
                "original_url": url,
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
    """Lightweight HTTP-fetch fallback when Playwright/crawl4ai is unavailable."""
    if not await is_safe_url_async(url):
        return {"success": False, "error": "Invalid or blocked URL (SSRF prevention)", "url": url}
    try:
        import httpx
        from bs4 import BeautifulSoup
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            max_redirects=MAX_REDIRECTS,
            headers={"User-Agent": "NeXifyAI-Research/1.0 (+https://nexify-automate.com)"},
        ) as c:
            r = await c.get(url)
            # Check if redirect target is safe
            final_url = str(r.url)
            if final_url != url and not await is_safe_url_async(final_url):
                logger.warning(f"SSRF blocked redirect in httpx fallback: {final_url}")
                return {"success": False, "error": "Redirect target blocked (SSRF prevention)", "url": url, "blocked_redirect": final_url}
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
                "url": final_url,
                "original_url": url,
                "title": title,
                "description": description,
                "content": text,
                "content_length": len(text),
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "method": "httpx_fallback",
            }
    except httpx.InvalidURL:
        logger.warning(f"httpx fallback invalid URL: {url}")
        return {"success": False, "error": "Invalid URL", "url": url}
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
