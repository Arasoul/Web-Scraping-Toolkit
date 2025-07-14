"""
Web Scraping and Analysis Toolkit
"""

from .web_scraper import WebScraper
from .config import Config
from .crawlability_analyzer import CrawlabilityAnalyzer
from .content_extractor import ContentExtractor
from .js_handler import JavaScriptHandler
from .report_generator import ReportGenerator

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    'WebScraper',
    'Config',
    'CrawlabilityAnalyzer', 
    'ContentExtractor',
    'JavaScriptHandler',
    'ReportGenerator'
]
