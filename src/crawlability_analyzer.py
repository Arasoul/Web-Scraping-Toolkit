"""
Crawlability Analyzer
Analyzes website robots.txt and crawling permissions.
"""

import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Any
import logging


class CrawlabilityAnalyzer:
    """Analyzes website crawlability and robots.txt compliance."""
    
    def __init__(self, base_url: str, user_agent: str = "*"):
        """
        Initialize crawlability analyzer.
        
        Args:
            base_url: Base URL of the website to analyze
            user_agent: User agent string for robots.txt analysis
        """
        self.base_url = base_url
        self.user_agent = user_agent
        self.logger = logging.getLogger(__name__)
    
    def analyze_robots_txt(self, target_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze robots.txt file for crawling permissions.
        
        Args:
            target_path: Specific path to check for crawling permission
            
        Returns:
            Dictionary containing robots.txt analysis results
        """
        parsed_url = urlparse(self.base_url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code != 200:
                return self._create_error_result(
                    robots_url, "robots.txt not found or inaccessible"
                )
            
            robots_txt = response.text
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            rules = self._parse_robots_rules(robots_txt)
            sitemaps = self._extract_sitemaps(robots_txt)
            crawl_delay = self._extract_crawl_delay(robots_txt)
            
            allowed = None
            if target_path:
                full_url = urljoin(self.base_url, target_path)
                allowed = rp.can_fetch(self.user_agent, full_url)
            
            return {
                "status": "success",
                "robots_url": robots_url,
                "allowed": allowed,
                "rules": rules,
                "sitemaps": sitemaps,
                "crawl_delay": crawl_delay
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing robots.txt: {e}")
            return self._create_error_result(robots_url, str(e))
    
    def _parse_robots_rules(self, robots_txt: str) -> Dict[str, List[str]]:
        """Parse allow and disallow rules from robots.txt."""
        lines = robots_txt.splitlines()
        allow_rules = []
        disallow_rules = []
        applicable = False
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if line.lower().startswith("user-agent:"):
                ua = line.split(":", 1)[1].strip()
                applicable = (ua == "*" or ua.lower() == self.user_agent.lower())
            
            if applicable:
                if line.lower().startswith("allow:"):
                    allow_rules.append(line.split(":", 1)[1].strip())
                elif line.lower().startswith("disallow:"):
                    disallow_rules.append(line.split(":", 1)[1].strip())
        
        return {"allow": allow_rules, "disallow": disallow_rules}
    
    def _extract_sitemaps(self, robots_txt: str) -> List[str]:
        """Extract sitemap URLs from robots.txt."""
        sitemaps = []
        for line in robots_txt.splitlines():
            line = line.strip()
            if line.lower().startswith("sitemap:"):
                sitemaps.append(line.split(":", 1)[1].strip())
        return sitemaps
    
    def _extract_crawl_delay(self, robots_txt: str) -> Optional[float]:
        """Extract crawl delay from robots.txt."""
        for line in robots_txt.splitlines():
            line = line.strip()
            if line.lower().startswith("crawl-delay:"):
                try:
                    return float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
        return None
    
    def _create_error_result(self, robots_url: str, error_msg: str) -> Dict[str, Any]:
        """Create error result dictionary."""
        return {
            "status": f"error: {error_msg}",
            "robots_url": robots_url,
            "allowed": None,
            "rules": {"allow": [], "disallow": []},
            "sitemaps": [],
            "crawl_delay": None
        }
    
    def calculate_crawlability_score(self, analysis_result: Dict[str, Any]) -> int:
        """
        Calculate crawlability score based on robots.txt analysis.
        
        Args:
            analysis_result: Result from analyze_robots_txt()
            
        Returns:
            Crawlability score (0-100)
        """
        if analysis_result["status"] != "success":
            return 0
        
        rules = analysis_result.get("rules", {})
        allow_count = len(rules.get("allow", []))
        disallow_count = len(rules.get("disallow", []))
        total_rules = allow_count + disallow_count
        
        if total_rules == 0:
            return 100  # No restrictions
        
        allow_ratio = allow_count / total_rules
        sitemap_count = len(analysis_result.get("sitemaps", []))
        sitemap_bonus = min(sitemap_count * 5, 20)  # max +20 points
        
        score = int(allow_ratio * 80 + sitemap_bonus)
        return min(score, 100)
    
    def print_analysis_summary(self, result: Dict[str, Any]) -> None:
        """Print formatted analysis summary."""
        print("\\n" + "=" * 60)
        print("🔍 Robots.txt Analysis Summary")
        print("=" * 60)
        print(f"URL: {result['robots_url']}")
        print(f"Status: {result['status']}")
        
        allowed = result['allowed']
        if allowed is not None:
            print(f"Crawling Allowed: {'✅ Yes' if allowed else '❌ No'}")
        else:
            print("Crawling Allowed: Unknown")
        
        rules = result.get('rules', {})
        print("\\n📜 Crawl Rules:")
        
        print("\\n✅ Allowed Paths:")
        allow_rules = rules.get('allow', [])
        if allow_rules:
            for path in allow_rules:
                print(f"  - {path}")
        else:
            print("  None")
        
        print("\\n❌ Disallowed Paths:")
        disallow_rules = rules.get('disallow', [])
        if disallow_rules:
            for path in disallow_rules:
                print(f"  - {path}")
        else:
            print("  None")
        
        print("\\n🕓 Crawl Delay:")
        delay = result.get('crawl_delay')
        print(f"  {delay if delay is not None else 'Not specified'}")
        
        print("\\n🗺️ Sitemap Links:")
        sitemaps = result.get('sitemaps', [])
        if sitemaps:
            for idx, sitemap in enumerate(sitemaps, 1):
                print(f"  {idx}. {sitemap}")
        else:
            print("  None")
        
        print("=" * 60 + "\\n")
