"""
Report Generator and Data Export
Generates analysis reports and exports data in various formats.
"""

import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging


class ReportGenerator:
    """Generates analysis reports and exports data."""
    
    def __init__(self, config):
        """
        Initialize report generator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.output_dir = config.get_output_directory()
        self.logger = logging.getLogger(__name__)
    
    def export_articles_to_csv(self, articles: List[Dict[str, Any]], 
                              filename: Optional[str] = None) -> Path:
        """
        Export articles to CSV format.
        
        Args:
            articles: List of article dictionaries
            filename: Output filename (optional)
            
        Returns:
            Path to the created CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"articles_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        if not articles:
            self.logger.warning("No articles to export")
            return filepath
        
        # Prepare data for CSV
        csv_data = []
        for article in articles:
            row = {
                'title': article.get('title', ''),
                'link': article.get('link', ''),
                'summary': article.get('summary', ''),
                'published_at': article.get('published_at', ''),
                'category': article.get('category', ''),
                'image': article.get('image', ''),
                'content': self._join_content(article.get('content', []))
            }
            csv_data.append(row)
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
        
        self.logger.info(f"Exported {len(articles)} articles to {filepath}")
        return filepath
    
    def export_to_json(self, data: Dict[str, Any], 
                      filename: Optional[str] = None) -> Path:
        """
        Export data to JSON format.
        
        Args:
            data: Data dictionary to export
            filename: Output filename (optional)
            
        Returns:
            Path to the created JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Exported data to {filepath}")
        return filepath
    
    def generate_analysis_summary(self, articles: List[Dict[str, Any]], 
                                crawlability_result: Dict[str, Any],
                                sitemap_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive analysis summary.
        
        Args:
            articles: List of extracted articles
            crawlability_result: Results from crawlability analysis
            sitemap_structure: Sitemap structure (optional)
            
        Returns:
            Analysis summary dictionary
        """
        summary = {
            'generation_time': datetime.now().isoformat(),
            'website_url': self.config.get('base_url'),
            'total_articles': len(articles),
            'crawlability_analysis': crawlability_result,
            'content_analysis': self._analyze_content(articles),
            'recommendations': self._generate_recommendations(articles, crawlability_result)
        }
        
        if sitemap_structure:
            summary['sitemap_structure'] = sitemap_structure
        
        return summary
    
    def _analyze_content(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze extracted content for insights."""
        if not articles:
            return {'error': 'No articles to analyze'}
        
        # Convert to DataFrame for easier analysis
        df = self._articles_to_dataframe(articles)
        
        analysis = {
            'total_articles': len(df),
            'date_range': self._get_date_range(df),
            'category_distribution': self._get_category_distribution(df),
            'content_statistics': self._get_content_statistics(df),
            'top_keywords': self._extract_top_keywords(df)
        }
        
        return analysis
    
    def _articles_to_dataframe(self, articles: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert articles list to pandas DataFrame."""
        df_data = []
        for article in articles:
            row = {
                'title': article.get('title', ''),
                'published_at': article.get('published_at', ''),
                'category': article.get('category', ''),
                'content_length': len(self._join_content(article.get('content', [])))
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Convert date column
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        
        return df
    
    def _get_date_range(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get date range of articles."""
        if 'published_at' not in df.columns or df['published_at'].isna().all():
            return {'error': 'No valid dates found'}
        
        valid_dates = df['published_at'].dropna()
        return {
            'earliest': valid_dates.min().isoformat() if not valid_dates.empty else None,
            'latest': valid_dates.max().isoformat() if not valid_dates.empty else None,
            'total_days': (valid_dates.max() - valid_dates.min()).days if len(valid_dates) > 1 else 0
        }
    
    def _get_category_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get distribution of article categories."""
        if 'category' not in df.columns:
            return {}
        
        return df['category'].value_counts().head(10).to_dict()
    
    def _get_content_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get content length statistics."""
        if 'content_length' not in df.columns:
            return {}
        
        stats = df['content_length'].describe()
        return {
            'average_length': int(stats['mean']) if not pd.isna(stats['mean']) else 0,
            'median_length': int(stats['50%']) if not pd.isna(stats['50%']) else 0,
            'min_length': int(stats['min']) if not pd.isna(stats['min']) else 0,
            'max_length': int(stats['max']) if not pd.isna(stats['max']) else 0,
            'total_content': int(df['content_length'].sum())
        }
    
    def _extract_top_keywords(self, df: pd.DataFrame, top_n: int = 10) -> List[Dict[str, Any]]:
        """Extract top keywords from article titles."""
        if 'title' not in df.columns:
            return []
        
        # Simple keyword extraction (you might want to use more sophisticated NLP)
        import re
        
        all_words = []
        for title in df['title'].dropna():
            # Extract words (4+ characters, alphabetic only)
            words = re.findall(r'\\b[a-zA-Z]{4,}\\b', title.lower())
            all_words.extend(words)
        
        # Count and return top keywords
        word_counts = Counter(all_words)
        return [{'word': word, 'count': count} for word, count in word_counts.most_common(top_n)]
    
    def _generate_recommendations(self, articles: List[Dict[str, Any]], 
                                crawlability_result: Dict[str, Any]) -> List[str]:
        """Generate scraping recommendations based on analysis."""
        recommendations = []
        
        # Based on crawlability
        if crawlability_result.get('status') == 'success':
            crawl_delay = crawlability_result.get('crawl_delay')
            if crawl_delay:
                recommendations.append(f"Respect crawl delay of {crawl_delay} seconds between requests")
            
            disallowed = crawlability_result.get('rules', {}).get('disallow', [])
            if disallowed:
                recommendations.append("Check robots.txt disallowed paths before crawling")
        
        # Based on content
        if articles:
            avg_content_length = sum(len(self._join_content(a.get('content', []))) for a in articles) / len(articles)
            if avg_content_length > 5000:
                recommendations.append("Consider using pagination or chunking for large content")
        
        # General recommendations
        recommendations.extend([
            "Implement rate limiting to be respectful to the server",
            "Use proper error handling and retry mechanisms",
            "Monitor for website structure changes",
            "Consider using caching to avoid duplicate requests"
        ])
        
        return recommendations
    
    def _join_content(self, content: List[str]) -> str:
        """Join content paragraphs into a single string."""
        if isinstance(content, list):
            return ' '.join(content)
        return str(content) if content else ''
    
    def create_visualization(self, articles: List[Dict[str, Any]], 
                           output_filename: Optional[str] = None) -> Optional[Path]:
        """
        Create visualizations from article data.
        
        Args:
            articles: List of article dictionaries
            output_filename: Output filename for the plot
            
        Returns:
            Path to the created visualization file
        """
        if not articles:
            self.logger.warning("No articles to visualize")
            return None
        
        try:
            df = self._articles_to_dataframe(articles)
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Web Scraping Analysis Report', fontsize=16)
            
            # 1. Articles over time
            if 'published_at' in df.columns and not df['published_at'].isna().all():
                df['date'] = df['published_at'].dt.date
                date_counts = df['date'].value_counts().sort_index()
                axes[0, 0].plot(date_counts.index, date_counts.values)
                axes[0, 0].set_title('Articles Over Time')
                axes[0, 0].tick_params(axis='x', rotation=45)
            else:
                axes[0, 0].text(0.5, 0.5, 'No date data available', ha='center', va='center')
                axes[0, 0].set_title('Articles Over Time (No Data)')
            
            # 2. Category distribution
            if 'category' in df.columns:
                category_counts = df['category'].value_counts().head(10)
                if not category_counts.empty:
                    axes[0, 1].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
                    axes[0, 1].set_title('Category Distribution')
                else:
                    axes[0, 1].text(0.5, 0.5, 'No category data', ha='center', va='center')
                    axes[0, 1].set_title('Category Distribution (No Data)')
            
            # 3. Content length distribution
            if 'content_length' in df.columns:
                axes[1, 0].hist(df['content_length'], bins=20, edgecolor='black')
                axes[1, 0].set_title('Content Length Distribution')
                axes[1, 0].set_xlabel('Content Length (characters)')
                axes[1, 0].set_ylabel('Frequency')
            
            # 4. Summary statistics
            stats_text = f"""
            Total Articles: {len(articles)}
            Date Range: {self._get_date_range(df).get('earliest', 'N/A')} to {self._get_date_range(df).get('latest', 'N/A')}
            Avg Content Length: {df['content_length'].mean():.0f} chars
            """
            axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center')
            axes[1, 1].set_title('Summary Statistics')
            axes[1, 1].axis('off')
            
            plt.tight_layout()
            
            # Save plot
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"analysis_visualization_{timestamp}.png"
            
            output_path = self.output_dir / output_filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Created visualization: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating visualization: {e}")
            return None
    
    def print_summary_report(self, summary: Dict[str, Any]) -> None:
        """Print formatted summary report to console."""
        print("\\n" + "=" * 80)
        print("📊 WEB SCRAPING ANALYSIS REPORT")
        print("=" * 80)
        
        print(f"🌐 Website: {summary.get('website_url', 'N/A')}")
        print(f"📅 Generated: {summary.get('generation_time', 'N/A')}")
        print(f"📰 Total Articles: {summary.get('total_articles', 0)}")
        
        # Crawlability section
        crawl = summary.get('crawlability_analysis', {})
        print(f"\\n🔍 CRAWLABILITY ANALYSIS")
        print(f"Status: {crawl.get('status', 'Unknown')}")
        if 'crawl_delay' in crawl and crawl['crawl_delay']:
            print(f"Crawl Delay: {crawl['crawl_delay']} seconds")
        
        # Content analysis section
        content = summary.get('content_analysis', {})
        if 'date_range' in content:
            date_range = content['date_range']
            print(f"\\n📅 DATE RANGE")
            print(f"From: {date_range.get('earliest', 'N/A')}")
            print(f"To: {date_range.get('latest', 'N/A')}")
        
        if 'category_distribution' in content:
            print(f"\\n🏷️ TOP CATEGORIES")
            for category, count in list(content['category_distribution'].items())[:5]:
                print(f"  - {category}: {count}")
        
        if 'top_keywords' in content:
            print(f"\\n🔑 TOP KEYWORDS")
            for kw in content['top_keywords'][:5]:
                print(f"  - {kw['word']}: {kw['count']}")
        
        # Recommendations
        recommendations = summary.get('recommendations', [])
        if recommendations:
            print(f"\\n💡 RECOMMENDATIONS")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
        
        print("=" * 80 + "\\n")
