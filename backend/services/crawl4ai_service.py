"""
NeXifyAI — Crawl4AI Service
Automatische Web-Crawling-Engine: Lead-Recherche, Wettbewerbsmonitoring, Content-Sammlung.
LLM-fertiges Markdown, JSON-Extraktion, Deep-Crawling.
"""
import os
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("nexifyai.services.crawl4ai")


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
        return {"success": False, "error": "crawl4ai nicht installiert", "url": url}
    except Exception as e:
        logger.error(f"Crawl4AI error for {url}: {e}")
        return {"success": False, "error": str(e)[:500], "url": url}


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
