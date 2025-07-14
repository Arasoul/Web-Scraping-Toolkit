"""
JavaScript and API Handler
Handles JavaScript-heavy content using Playwright and RSS feeds.
"""

import asyncio
import feedparser
import requests
from xml.etree import ElementTree as ET
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Any, Optional
import logging

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available. Install with: pip install playwright && playwright install")


class JavaScriptHandler:
    """Handles JavaScript-heavy content and RSS feeds."""
    
    def __init__(self, config):
        """
        Initialize JavaScript handler.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.base_url = config.get('base_url')
        self.logger = logging.getLogger(__name__)
    
    async def fetch_with_playwright(self, url: str) -> Optional[str]:
        """
        Fetch page content using Playwright for JavaScript rendering.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content string or None if failed
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available. Cannot fetch JavaScript content.")
            return None
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config.get('headless_browser', True)
                )
                page = await browser.new_page()
                
                # Set user agent
                await page.set_extra_http_headers({
                    'User-Agent': self.config.get('user_agent')
                })
                
                await page.goto(url, timeout=self.config.get('timeout', 30) * 1000)
                content = await page.content()
                await browser.close()
                
                return content
                
        except Exception as e:
            self.logger.error(f"Error fetching with Playwright: {e}")
            return None
    
    def fetch_rss_feeds(self, rss_urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS feeds.
        
        Args:
            rss_urls: List of RSS feed URLs. If None, uses config.
            
        Returns:
            List of RSS feed entries
        """
        if rss_urls is None:
            rss_urls = self.config.get('rss_feeds', [])
        
        if not rss_urls:
            self.logger.info("No RSS feeds configured")
            return []
        
        all_entries = []
        
        for rss_url in rss_urls:
            try:
                self.logger.info(f"Fetching RSS feed: {rss_url}")
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries:
                    entry_data = {
                        'title': getattr(entry, 'title', ''),
                        'link': getattr(entry, 'link', ''),
                        'summary': getattr(entry, 'summary', ''),
                        'published': getattr(entry, 'published', ''),
                        'source': rss_url,
                        'feed_title': getattr(feed.feed, 'title', '')
                    }
                    all_entries.append(entry_data)
                    
                self.logger.info(f"Fetched {len(feed.entries)} entries from RSS feed")
                
            except Exception as e:
                self.logger.error(f"Error fetching RSS feed {rss_url}: {e}")
                continue
        
        return all_entries
    
    def fetch_sitemap_urls(self, sitemap_url: str, max_urls: int = 1000) -> List[str]:
        """
        Fetch URLs from sitemap.
        
        Args:
            sitemap_url: URL of the sitemap
            max_urls: Maximum number of URLs to return
            
        Returns:
            List of URLs from sitemap
        """
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Handle both sitemap index and regular sitemap
            loc_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            
            urls = [elem.text for elem in loc_elements if elem.text]
            
            # If this is a sitemap index, fetch sub-sitemaps
            if any('sitemap' in url.lower() for url in urls[:5]):
                self.logger.info("Detected sitemap index, fetching sub-sitemaps")
                sub_urls = []
                
                for sub_sitemap_url in urls[:10]:  # Limit sub-sitemaps
                    try:
                        sub_urls.extend(self.fetch_sitemap_urls(sub_sitemap_url, max_urls//10))
                    except Exception as e:
                        self.logger.warning(f"Failed to fetch sub-sitemap {sub_sitemap_url}: {e}")
                        continue
                
                urls = sub_urls
            
            return urls[:max_urls]
            
        except Exception as e:
            self.logger.error(f"Error fetching sitemap {sitemap_url}: {e}")
            return []
    
    def build_sitemap_structure(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        Build hierarchical sitemap structure from URLs.
        
        Args:
            urls: List of URLs
            
        Returns:
            Dictionary representing sitemap structure
        """
        sitemap = {}
        
        for url in urls:
            try:
                parsed = urlparse(url)
                path_parts = [part for part in parsed.path.strip("/").split("/") if part]
                
                if not path_parts:
                    continue
                
                # Group by first path component
                parent = path_parts[0].capitalize()
                
                if len(path_parts) > 1:
                    child = path_parts[1].capitalize()
                    sitemap.setdefault(parent, set()).add(child)
                else:
                    sitemap.setdefault(parent, set()).add("Index")
                    
            except Exception:
                continue
        
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in sitemap.items()}
    
    def analyze_javascript_content(self, url: str) -> Dict[str, Any]:
        """
        Analyze JavaScript content on a page.
        
        Args:
            url: URL to analyze
            
        Returns:
            Analysis results
        """
        try:
            # First try regular requests
            response = requests.get(url, timeout=30)
            static_content = response.text
            
            # Then try with Playwright if available
            if PLAYWRIGHT_AVAILABLE:
                js_content = asyncio.run(self.fetch_with_playwright(url))
            else:
                js_content = None
            
            analysis = {
                'url': url,
                'static_content_length': len(static_content),
                'requires_javascript': False,
                'content_difference': 0
            }
            
            if js_content:
                analysis['js_content_length'] = len(js_content)
                analysis['content_difference'] = len(js_content) - len(static_content)
                analysis['requires_javascript'] = analysis['content_difference'] > 1000
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing JavaScript content: {e}")
            return {
                'url': url,
                'error': str(e),
                'requires_javascript': None
            }
