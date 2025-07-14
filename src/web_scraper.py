"""
Main Web Scraper Class
Orchestrates all scraping and analysis components.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .config import Config
from .crawlability_analyzer import CrawlabilityAnalyzer
from .content_extractor import ContentExtractor
from .js_handler import JavaScriptHandler
from .report_generator import ReportGenerator


class WebScraper:
    """Main web scraper that coordinates all components."""
    
    def __init__(self, config_path: str = "config.json", log_level: str = "INFO"):
        """
        Initialize web scraper.
        
        Args:
            config_path: Path to configuration file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = Config(config_path)
        self.base_url = self.config.get('base_url')
        
        # Initialize components
        self.crawlability_analyzer = CrawlabilityAnalyzer(
            self.base_url, 
            self.config.get('user_agent')
        )
        self.content_extractor = ContentExtractor(self.config)
        self.js_handler = JavaScriptHandler(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        self.logger.info(f"WebScraper initialized for {self.base_url}")
    
    def setup_logging(self, log_level: str) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('webscraper.log')
            ]
        )
    
    def analyze_robots_txt(self, target_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze website's robots.txt file.
        
        Args:
            target_path: Specific path to check for crawling permission
            
        Returns:
            Robots.txt analysis results
        """
        self.logger.info("Analyzing robots.txt...")
        result = self.crawlability_analyzer.analyze_robots_txt(target_path)
        
        if self.config.get('respect_robots_txt', True) and result.get('allowed') is False:
            self.logger.warning(f"Crawling not allowed for path: {target_path}")
        
        return result
    
    def extract_articles(self, max_articles: Optional[int] = None,
                        max_show_more_clicks: int = 10) -> List[Dict[str, Any]]:
        """
        Extract articles from the website.
        
        Args:
            max_articles: Maximum number of articles to extract
            max_show_more_clicks: Maximum times to click "show more" button
            
        Returns:
            List of extracted articles
        """
        self.logger.info("Extracting articles...")
        
        # Check robots.txt first if configured
        if self.config.get('respect_robots_txt', True):
            robots_result = self.analyze_robots_txt(self.config.get('news_section_path', '/news'))
            if robots_result.get('allowed') is False:
                self.logger.error("Crawling not allowed according to robots.txt")
                return []
        
        articles = self.content_extractor.extract_articles(max_articles, max_show_more_clicks)
        self.logger.info(f"Extracted {len(articles)} articles")
        
        return articles
    
    def fetch_rss_feeds(self, rss_urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetch RSS feed entries.
        
        Args:
            rss_urls: List of RSS feed URLs
            
        Returns:
            List of RSS feed entries
        """
        self.logger.info("Fetching RSS feeds...")
        entries = self.js_handler.fetch_rss_feeds(rss_urls)
        self.logger.info(f"Fetched {len(entries)} RSS entries")
        return entries
    
    def analyze_sitemap(self, sitemap_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze website sitemap.
        
        Args:
            sitemap_url: URL of the sitemap (if None, tries to find from robots.txt)
            
        Returns:
            Sitemap analysis results
        """
        self.logger.info("Analyzing sitemap...")
        
        if not sitemap_url:
            # Try to get sitemap from robots.txt
            robots_result = self.analyze_robots_txt()
            sitemaps = robots_result.get('sitemaps', [])
            if sitemaps:
                sitemap_url = sitemaps[0]
            else:
                # Try common sitemap location
                sitemap_url = f"{self.base_url.rstrip('/')}/sitemap.xml"
        
        if sitemap_url:
            urls = self.js_handler.fetch_sitemap_urls(sitemap_url)
            structure = self.js_handler.build_sitemap_structure(urls)
            
            return {
                'sitemap_url': sitemap_url,
                'total_urls': len(urls),
                'structure': structure,
                'sample_urls': urls[:10]  # First 10 URLs as sample
            }
        else:
            return {
                'sitemap_url': None,
                'total_urls': 0,
                'structure': {},
                'sample_urls': []
            }
    
    def run_full_analysis(self, max_articles: Optional[int] = None,
                         include_rss: bool = True,
                         include_sitemap: bool = True,
                         create_visualizations: bool = True) -> Dict[str, Any]:
        """
        Run complete analysis of the website.
        
        Args:
            max_articles: Maximum number of articles to extract
            include_rss: Whether to fetch RSS feeds
            include_sitemap: Whether to analyze sitemap
            create_visualizations: Whether to create visualizations
            
        Returns:
            Complete analysis results
        """
        self.logger.info("Starting full website analysis...")
        
        results = {}
        
        # 1. Analyze robots.txt
        results['robots_analysis'] = self.analyze_robots_txt()
        crawlability_score = self.crawlability_analyzer.calculate_crawlability_score(
            results['robots_analysis']
        )
        results['crawlability_score'] = crawlability_score
        
        # 2. Extract articles
        results['articles'] = self.extract_articles(max_articles)
        
        # 3. Fetch RSS feeds (optional)
        if include_rss:
            results['rss_entries'] = self.fetch_rss_feeds()
        
        # 4. Analyze sitemap (optional)
        if include_sitemap:
            results['sitemap_analysis'] = self.analyze_sitemap()
        
        # 5. Generate comprehensive report
        analysis_summary = self.report_generator.generate_analysis_summary(
            results['articles'],
            results['robots_analysis'],
            results.get('sitemap_analysis', {}).get('structure')
        )
        results['analysis_summary'] = analysis_summary
        
        # 6. Export data
        self.export_results(results)
        
        # 7. Create visualizations (optional)
        if create_visualizations and results['articles']:
            viz_path = self.report_generator.create_visualization(results['articles'])
            if viz_path:
                results['visualization_path'] = str(viz_path)
        
        # Print summary
        self.report_generator.print_summary_report(analysis_summary)
        
        self.logger.info("Full analysis completed successfully")
        return results
    
    def export_results(self, results: Dict[str, Any]) -> Dict[str, Path]:
        """
        Export results in configured formats.
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Dictionary of export file paths
        """
        export_paths = {}
        output_formats = self.config.get('output_formats', ['json'])
        
        # Export articles to CSV if requested
        if 'csv' in output_formats and results.get('articles'):
            csv_path = self.report_generator.export_articles_to_csv(results['articles'])
            export_paths['csv'] = csv_path
        
        # Export full results to JSON if requested
        if 'json' in output_formats:
            # Prepare data for JSON export (remove non-serializable objects)
            json_data = {
                'analysis_summary': results.get('analysis_summary', {}),
                'crawlability_score': results.get('crawlability_score', 0),
                'robots_analysis': results.get('robots_analysis', {}),
                'total_articles': len(results.get('articles', [])),
                'sitemap_analysis': results.get('sitemap_analysis', {}),
                'rss_entries_count': len(results.get('rss_entries', []))
            }
            
            json_path = self.report_generator.export_to_json(json_data)
            export_paths['json'] = json_path
        
        return export_paths
    
    def get_recommendations(self) -> List[str]:
        """Get scraping recommendations based on current configuration."""
        robots_result = self.analyze_robots_txt()
        return self.report_generator._generate_recommendations([], robots_result)
