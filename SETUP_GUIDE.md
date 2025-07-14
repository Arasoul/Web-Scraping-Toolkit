# Installation and Setup Guide

## Quick Start with Streamlit App

The easiest way to use this project is through the interactive Streamlit dashboard:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium  # Optional: for JavaScript support
```

### 2. Launch the Web App
```bash
streamlit run app.py
```
Or use the convenience script:
```bash
python run_app.py
```

### 3. Access the Dashboard
Open your browser and go to: http://localhost:8501

The Streamlit app provides:
- **Interactive Configuration**: Set up scraping parameters through a user-friendly interface
- **Real-time Extraction**: Monitor progress with live updates
- **Data Visualization**: Charts and graphs for analyzing content
- **Export Options**: Download results in JSON or CSV format

## Manual Setup (Alternative)

If you prefer to use the Python API directly:

### 1. Install Required Dependencies

Run these commands in your terminal:

```bash
# Install all required packages
pip install -r requirements.txt

# If you want JavaScript support, also install:
pip install playwright
playwright install chromium
```

### 2. Alternative: Install Individual Packages

If you prefer to install packages individually:

```bash
pip install streamlit>=1.28.0
pip install plotly>=5.17.0
pip install selenium>=4.15.0
pip install playwright>=1.40.0
pip install feedparser>=6.0.10
pip install beautifulsoup4>=4.12.0
pip install requests>=2.31.0
pip install pandas>=2.0.0
pip install matplotlib>=3.7.0
pip install seaborn>=0.12.0
pip install lxml>=4.9.0
```

### 3. For Chrome/Selenium Issues

Make sure you have Chrome browser installed, or install ChromeDriver:

```bash
pip install webdriver-manager
```

### 4. Verify Installation

Run this to check if everything is installed:

```python
# Test script to verify installations
try:
    import requests
    import beautifulsoup4
    import pandas
    import matplotlib
    print("✅ Core packages installed")
except ImportError as e:
    print(f"❌ Missing core package: {e}")

try:
    import selenium
    print("✅ Selenium installed")
except ImportError:
    print("⚠️ Selenium not installed - some features will be limited")

try:
    import playwright
    print("✅ Playwright installed")
except ImportError:
    print("⚠️ Playwright not installed - JavaScript handling limited")

try:
    import feedparser
    print("✅ Feedparser installed")
except ImportError:
    print("⚠️ Feedparser not installed - RSS features limited")
```

### 5. Files That Should NOT Be Deleted

All current files are necessary:

- `src/` - Core application code
- `requirements.txt` - Dependency list
- `config.example.json` - Configuration template
- `README.md` - Documentation
- `LICENSE` - Open source license
- `.gitignore` - Git ignore rules
- `IR_Project.ipynb` - Demo notebook
- `example.py` - Usage example
- `output/` - Output directory

### 6. Common Issues and Solutions

**Red/Error Files Usually Mean:**
- Missing Python packages (install with pip)
- Import errors (check package names)
- Type checking issues (can be ignored for now)

**To Clean Up (ONLY if needed):**
- Any `.pyc` files (Python bytecode)
- `__pycache__/` directories  
- Temporary files like `temp_config.json`

**DO NOT DELETE:**
- Any `.py` files in `src/`
- Configuration files
- Documentation files
- The notebook file

After installing the dependencies, the red coloring should disappear and your code will be ready for GitHub! 🚀

## Using the Streamlit Web App

### Features
- **🖥️ Interactive Interface**: No command line needed
- **⚙️ Visual Configuration**: Set up scraping parameters through forms
- **📊 Real-time Analytics**: See charts and statistics of extracted data
- **💾 Easy Export**: Download results with one click
- **🔍 Live Preview**: See article previews as they're extracted

### Getting Started
1. Run `streamlit run app.py`
2. Configure your target website in the sidebar
3. Click "Start Extraction" to begin scraping
4. View results in the "Results" tab
5. Export data in the "Export Data" tab

### Configuration Options
- **Base URL**: Target website to scrape
- **Max Articles**: Limit number of articles to extract
- **Crawl Delay**: Delay between requests (be respectful!)
- **CSS Selectors**: Customize how content is extracted
- **Browser Settings**: Headless mode, timeouts, etc.

### Tips for Best Results
- Start with a small number of articles (10-20) to test
- Increase crawl delay for large sites to avoid being blocked
- Use browser developer tools to find the right CSS selectors
- Check robots.txt before scraping any website
