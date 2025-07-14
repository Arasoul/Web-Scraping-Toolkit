"""
Example usage script for the Web Scraping Toolkit
Run this script to see a basic example of how to use the toolkit.
"""

from src.web_scraper import WebScraper
import json

def main():
    """Main example function."""
    print("🕷️ Web Scraping Toolkit - Example Usage")
    print("=" * 50)
    
    # Example configuration for a news website
    example_config = {
        "base_url": "https://example-news-site.com",
        "news_section_path": "/news",
        "max_articles": 20,
        "crawl_delay": 2,
        "output_formats": ["csv", "json"],
        "user_agent": "WebScraper/1.0 (Educational Research)",
        "timeout": 30,
        "headless_browser": True,
        "respect_robots_txt": True,
        "selectors": {
            "article_links": "article a[href*='/news/']",
            "title": "h1, .article-title, .headline",
            "content": "p, .article-content, .story-body",
            "date": "time, .publish-date, .timestamp",
            "category": ".category, .topic, .section",
            "image": ".article-image img, .featured-image img"
        },
        "rss_feeds": []
    }
    
    # Save example config
    with open("example_config.json", "w") as f:
        json.dump(example_config, f, indent=2)
    
    print("📝 Created example_config.json")
    print("💡 Update the base_url and selectors for your target website")
    print()
    
    try:
        # Initialize scraper
        scraper = WebScraper("example_config.json")
        
        # Quick robots.txt analysis
        print("🤖 Analyzing robots.txt...")
        robots_result = scraper.analyze_robots_txt()
        score = scraper.crawlability_analyzer.calculate_crawlability_score(robots_result)
        print(f"Crawlability Score: {score}/100")
        
        # Get recommendations
        recommendations = scraper.get_recommendations()
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n✅ Basic analysis complete!")
        print(f"📖 See README.md for full usage instructions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 Make sure to update the base_url in example_config.json")

if __name__ == "__main__":
    main()
