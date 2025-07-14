"""
Content Extractor
Extracts articles and content from websites using Selenium.
"""

import time
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
import logging

# Handle optional selenium imports
try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.common.by import By  # type: ignore
    from selenium.webdriver.chrome.options import Options  # type: ignore
    from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
    from selenium.webdriver.support import expected_conditions as EC  # type: ignore
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available. Article extraction will be limited to static content.")


class ContentExtractor:
    """Extracts articles and content from websites."""
    
    def __init__(self, config):
        """
        Initialize content extractor.
        
        Args:
            config: Configuration object containing selectors and settings
        """
        self.config = config
        self.base_url = config.get('base_url')
        self.selectors = config.get_selectors()
        self.headers = {'User-Agent': config.get('user_agent')}
        self.logger = logging.getLogger(__name__)
    
    def extract_articles(self, max_articles: Optional[int] = None, 
                        max_show_more_clicks: int = 10) -> List[Dict[str, Any]]:
        """
        Extract articles from the website.
        
        Args:
            max_articles: Maximum number of articles to extract
            max_show_more_clicks: Maximum times to click "show more" button
            
        Returns:
            List of article dictionaries
        """
        if not SELENIUM_AVAILABLE:
            self.logger.error("Selenium not available. Cannot extract articles with dynamic content.")
            self.logger.info("Install selenium with: pip install selenium")
            return []
            
        max_articles = max_articles or self.config.get('max_articles', 50)
        
        chrome_options = self._get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            news_url = urljoin(self.base_url, self.config.get('news_section_path', '/news'))
            driver.get(news_url)
            time.sleep(3)
            
            if max_show_more_clicks > 0:
                self._click_show_more_button(driver, max_show_more_clicks)
            
            articles = self._extract_articles_from_page(driver)
            
            if max_articles and len(articles) > max_articles:
                articles = articles[:max_articles]
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error extracting articles: {e}")
            return []
        finally:
            driver.quit()
    
    def _get_chrome_options(self) -> Options:
        """Get Chrome browser options."""
        options = Options()
        if self.config.get('headless_browser', True):
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return options
    
    def _click_show_more_button(self, driver, max_clicks: int) -> None:
        """Click 'show more' button to load additional content."""
        clicks = 0
        
        # Common selectors for "show more" buttons
        show_more_selectors = [
            "button[id*='show-more']",
            "button[class*='show-more']",
            "button[class*='load-more']",
            ".show-more-button",
            ".load-more-button",
            "button:contains('Show More')",
            "button:contains('Load More')",
            "button:contains('عرض المزيد')"  # Arabic
        ]
        
        while clicks < max_clicks:
            try:
                # Scroll to bottom first
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                button_found = False
                for selector in show_more_selectors:
                    try:
                        button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", button)
                        
                        clicks += 1
                        button_found = True
                        self.logger.info(f"Clicked show more button ({clicks})")
                        time.sleep(self.config.get('crawl_delay', 2))
                        break
                        
                    except Exception:
                        continue
                
                if not button_found:
                    break
                    
            except Exception as e:
                self.logger.debug(f"No more show more buttons found: {e}")
                break
        
        self.logger.info(f"Finished clicking show more buttons. Total clicks: {clicks}")
    
    def _extract_articles_from_page(self, driver) -> List[Dict[str, Any]]:
        """Extract article information from the current page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find article links using configured selector
        article_selector = self.selectors.get('article_links', 'article a')
        article_links = soup.select(article_selector)
        
        seen_links = set()
        articles = []
        
        self.logger.info(f"Found {len(article_links)} potential article links")
        
        for tag in article_links:
            href = tag.get("href")
            if not href:
                continue
            
            # Ensure href is a string
            if isinstance(href, list):
                href = href[0] if href else ""
                
            link = urljoin(self.base_url, href)
            title = tag.get_text(strip=True)
            
            if link in seen_links or not title:
                continue
            
            seen_links.add(link)
            
            try:
                article_details = self._extract_article_details(link)
                if article_details:
                    article_info = {
                        "title": title,
                        "link": link,
                        **article_details
                    }
                    articles.append(article_info)
                    self.logger.debug(f"Extracted article: {title}")
                    
                    # Add delay between requests
                    time.sleep(self.config.get('crawl_delay', 1))
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract article {link}: {e}")
                continue
        
        self.logger.info(f"Successfully extracted {len(articles)} articles")
        return articles
    
    def _extract_article_details(self, article_url: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information from a single article."""
        try:
            response = requests.get(
                article_url, 
                headers=self.headers, 
                timeout=self.config.get('timeout', 30)
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                "summary": self._extract_summary(soup),
                "published_at": self._extract_publish_date(soup),
                "category": self._extract_category(soup),
                "image": self._extract_image(soup),
                "content": self._extract_content(soup)
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to extract details from {article_url}: {e}")
            return None
    
    def _extract_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article summary/description."""
        meta_desc = soup.select_one("meta[name='description']")
        if meta_desc:
            content = meta_desc.get('content')
            return content[0] if isinstance(content, list) else content
        
        # Try other common meta tags
        for selector in ["meta[property='og:description']", "meta[name='twitter:description']"]:
            meta_tag = soup.select_one(selector)
            if meta_tag:
                content = meta_tag.get('content')
                return content[0] if isinstance(content, list) else content
        
        return None
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article publish date."""
        # Try configured selector first
        date_selector = self.selectors.get('date', 'time')
        time_tag = soup.select_one(date_selector)
        
        if time_tag:
            # Check for datetime attribute
            if time_tag.has_attr('datetime'):
                datetime_attr = time_tag['datetime']
                return datetime_attr[0] if isinstance(datetime_attr, list) else datetime_attr
            
            # Try to parse text content
            text = time_tag.get_text(strip=True)
            if text:
                return self._parse_date_string(text)
        
        # Try other common date patterns
        date_patterns = [
            r'\\d{4}-\\d{2}-\\d{2}',
            r'\\d{1,2}/\\d{1,2}/\\d{4}',
            r'\\d{1,2}-\\d{1,2}-\\d{4}'
        ]
        
        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                return self._parse_date_string(match.group())
        
        return None
    
    def _parse_date_string(self, date_str: str) -> Optional[str]:
        """Parse various date string formats."""
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.date().isoformat()
            except ValueError:
                continue
        
        return date_str  # Return original if parsing fails
    
    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article category."""
        category_selector = self.selectors.get('category', '.category')
        category_tag = soup.select_one(category_selector)
        
        if category_tag:
            return category_tag.get_text(strip=True)
        
        # Try other common category selectors
        for selector in [".topic", ".section", "[class*='category']", "[class*='topic']"]:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(strip=True)
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article featured image."""
        image_selector = self.selectors.get('image', '.article-image img')
        img_tag = soup.select_one(image_selector)
        
        if img_tag and img_tag.has_attr("src"):
            src = img_tag["src"]
            src_str = src[0] if isinstance(src, list) else src
            return urljoin(self.base_url, src_str)
        
        # Try other common image selectors
        for selector in [
            ".featured-image img",
            ".hero-image img", 
            "meta[property='og:image']",
            ".article-header img"
        ]:
            tag = soup.select_one(selector)
            if tag:
                src = tag.get('src') or tag.get('content')
                if src:
                    src_str = src[0] if isinstance(src, list) else src
                    return urljoin(self.base_url, src_str)
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> List[str]:
        """Extract article content paragraphs."""
        content_selector = self.selectors.get('content', 'p')
        paragraphs = soup.select(content_selector)
        
        clean_paragraphs = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short paragraphs
                clean_paragraphs.append(text)
        
        return clean_paragraphs
