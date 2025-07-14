# Web Scraping and Analysis Toolkit

A comprehensive web scraping and analysis toolkit that provides crawlability analysis, content extraction, JavaScript handling, and data visualization capabilities with an interactive Streamlit dashboard.

## Features

- 🤖 **Robots.txt Analysis**: Analyze website crawling permissions and rules
- 📰 **Content Extraction**: Extract articles with metadata (title, summary, date, category, images)
- 🌐 **JavaScript Support**: Handle dynamic content with Selenium and Playwright
- 📡 **RSS Feed Parsing**: Parse and analyze RSS feeds
- 🗺️ **Sitemap Analysis**: Analyze website structure from sitemaps
- 📊 **Data Export**: Export data to CSV and JSON formats
- 📈 **Crawlability Scoring**: Generate crawlability scores and recommendations
- 🖥️ **Streamlit Dashboard**: Interactive web interface for configuration and visualization

## Installation

### Prerequisites
- Python 3.8+
- Chrome browser (for Selenium)

### Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Streamlit Web App (Recommended)
Launch the interactive dashboard:
```bash
streamlit run app.py
```

The web app provides:
- **Interactive Configuration**: Set up scraping parameters through a user-friendly interface
- **Real-time Extraction**: Monitor scraping progress with live updates
- **Data Visualization**: Charts and graphs for analyzing extracted content
- **Export Options**: Download results in JSON or CSV format

### Basic Example (Python API)
```python
from src.content_extractor import ContentExtractor
from src.config import Config

# Load configuration
config = Config.from_file("config.json")

# Initialize extractor
extractor = ContentExtractor(config)

# Extract articles
articles = extractor.extract_articles(max_articles=50)

# Process results
for article in articles:
    print(f"Title: {article['title']}")
    print(f"Link: {article['link']}")
```

### Configuration
Copy `config.example.json` to `config.json` and modify settings:
```json
{
  "base_url": "https://your-target-website.com",
  "max_articles": 100,
  "crawl_delay": 1,
  "output_format": ["csv", "json"],
  "user_agent": "WebScraper/1.0"
}
```

## Project Structure
```
├── src/
│   ├── crawlability_analyzer.py
│   ├── content_extractor.py
│   ├── js_handler.py
│   ├── report_generator.py
│   └── web_scraper.py
├── config/
│   ├── config.json
│   └── config.example.json
├── output/
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and research purposes. Please respect website terms of service and robots.txt files. Always implement appropriate delays and rate limiting.
