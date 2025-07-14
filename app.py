"""
Streamlit Web App for Content Extraction
Interactive dashboard for scraping and analyzing articles.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any
import logging

# Import our custom modules
from src.content_extractor import ContentExtractor
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_default_config():
    """Load default configuration."""
    return {
        "base_url": "https://example-news-site.com",
        "news_section_path": "/news",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "max_articles": 50,
        "crawl_delay": 2,
        "timeout": 30,
        "headless_browser": True,
        "selectors": {
            "article_links": "article a, .article-link, .news-item a",
            "title": "h1, .article-title, .news-title",
            "content": "p, .article-content p, .news-content p",
            "date": "time, .article-date, .news-date",
            "category": ".category, .topic, .section",
            "image": ".article-image img, .featured-image img"
        }
    }

def save_config_to_file(config_data: dict, filename: str = "config.json"):
    """Save configuration to file."""
    try:
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)
        st.success(f"Configuration saved to {filename}")
    except Exception as e:
        st.error(f"Failed to save configuration: {e}")

def load_config_from_file(filename: str = "config.json") -> dict:
    """Load configuration from file."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        else:
            return load_default_config()
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return load_default_config()

def display_articles_table(articles: List[Dict[str, Any]]):
    """Display articles in a formatted table."""
    if not articles:
        st.warning("No articles to display")
        return
    
    # Convert to DataFrame
    df_data = []
    for article in articles:
        df_data.append({
            "Title": article.get("title", "N/A"),
            "Category": article.get("category", "N/A"),
            "Published Date": article.get("published_at", "N/A"),
            "Summary": article.get("summary", "N/A")[:100] + "..." if article.get("summary") else "N/A",
            "Link": article.get("link", "N/A")
        })
    
    df = pd.DataFrame(df_data)
    
    # Display with clickable links
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Link": st.column_config.LinkColumn("Article Link"),
            "Title": st.column_config.TextColumn("Title", width="medium"),
            "Summary": st.column_config.TextColumn("Summary", width="large")
        }
    )

def create_visualizations(articles: List[Dict[str, Any]]):
    """Create visualizations for the articles data."""
    if not articles:
        return
    
    st.subheader("📊 Data Analysis")
    
    # Convert to DataFrame for analysis
    df_data = []
    for article in articles:
        df_data.append({
            "category": article.get("category", "Unknown"),
            "published_at": article.get("published_at", ""),
            "title_length": len(article.get("title", "")),
            "summary_length": len(article.get("summary", "")),
            "has_image": bool(article.get("image"))
        })
    
    df = pd.DataFrame(df_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution
        category_counts = df['category'].value_counts()
        if not category_counts.empty:
            fig_category = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Articles by Category"
            )
            st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # Articles with/without images
        image_counts = df['has_image'].value_counts()
        if not image_counts.empty:
            fig_images = px.bar(
                x=['With Images', 'Without Images'],
                y=[image_counts.get(True, 0), image_counts.get(False, 0)],
                title="Articles with Images"
            )
            st.plotly_chart(fig_images, use_container_width=True)
    
    # Title length distribution
    if not df['title_length'].empty:
        fig_title_length = px.histogram(
            df, 
            x='title_length', 
            title="Distribution of Title Lengths",
            labels={'title_length': 'Title Length (characters)'}
        )
        st.plotly_chart(fig_title_length, use_container_width=True)

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Content Extractor Dashboard",
        page_icon="📰",
        layout="wide"
    )
    
    st.title("📰 Content Extractor Dashboard")
    st.markdown("Extract and analyze articles from news websites")
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Load existing config
    config_data = load_config_from_file()
    
    # Configuration form
    with st.sidebar.form("config_form"):
        st.subheader("Website Settings")
        base_url = st.text_input("Base URL", value=config_data.get("base_url", ""))
        news_section_path = st.text_input("News Section Path", value=config_data.get("news_section_path", "/news"))
        
        st.subheader("Extraction Settings")
        max_articles = st.number_input("Max Articles", min_value=1, max_value=1000, value=config_data.get("max_articles", 50))
        max_show_more_clicks = st.number_input("Max 'Show More' Clicks", min_value=0, max_value=50, value=10)
        crawl_delay = st.slider("Crawl Delay (seconds)", min_value=1, max_value=10, value=config_data.get("crawl_delay", 2))
        headless_browser = st.checkbox("Headless Browser", value=config_data.get("headless_browser", True))
        
        st.subheader("CSS Selectors")
        article_links_selector = st.text_input(
            "Article Links Selector", 
            value=config_data.get("selectors", {}).get("article_links", "article a")
        )
        content_selector = st.text_input(
            "Content Selector", 
            value=config_data.get("selectors", {}).get("content", "p")
        )
        date_selector = st.text_input(
            "Date Selector", 
            value=config_data.get("selectors", {}).get("date", "time")
        )
        category_selector = st.text_input(
            "Category Selector", 
            value=config_data.get("selectors", {}).get("category", ".category")
        )
        
        submitted = st.form_submit_button("Update Configuration")
        
        if submitted:
            # Update config
            config_data.update({
                "base_url": base_url,
                "news_section_path": news_section_path,
                "max_articles": max_articles,
                "crawl_delay": crawl_delay,
                "headless_browser": headless_browser,
                "selectors": {
                    "article_links": article_links_selector,
                    "content": content_selector,
                    "date": date_selector,
                    "category": category_selector,
                    "title": config_data.get("selectors", {}).get("title", "h1"),
                    "image": config_data.get("selectors", {}).get("image", ".article-image img")
                }
            })
            
            save_config_to_file(config_data)
            st.rerun()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🚀 Extract Articles", "📊 Results", "📋 Export Data"])
    
    with tab1:
        st.header("Article Extraction")
        
        if not base_url:
            st.warning("Please configure the base URL in the sidebar before extracting articles.")
            return
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.info(f"**Target Website:** {base_url}")
            st.info(f"**Max Articles:** {max_articles}")
        
        with col2:
            extract_button = st.button("🚀 Start Extraction", type="primary")
        
        with col3:
            if st.button("💾 Save Config"):
                save_config_to_file(config_data)
        
        if extract_button:
            try:
                # Create config object
                config = Config.from_dict(config_data)
                
                # Initialize extractor
                with st.spinner("Initializing content extractor..."):
                    extractor = ContentExtractor(config)
                
                # Extract articles
                with st.spinner(f"Extracting articles from {base_url}... This may take a while."):
                    articles = extractor.extract_articles(
                        max_articles=max_articles,
                        max_show_more_clicks=max_show_more_clicks
                    )
                
                # Store results in session state
                st.session_state.articles = articles
                st.session_state.extraction_time = datetime.now()
                
                if articles:
                    st.success(f"✅ Successfully extracted {len(articles)} articles!")
                    st.balloons()
                else:
                    st.warning("No articles were extracted. Please check your configuration.")
                    
            except Exception as e:
                st.error(f"Error during extraction: {str(e)}")
                logger.error(f"Extraction error: {e}")
    
    with tab2:
        st.header("Extraction Results")
        
        if 'articles' in st.session_state and st.session_state.articles:
            articles = st.session_state.articles
            extraction_time = st.session_state.get('extraction_time', 'Unknown')
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Articles", len(articles))
            
            with col2:
                categories = set(article.get('category', 'Unknown') for article in articles)
                st.metric("Categories", len(categories))
            
            with col3:
                articles_with_images = sum(1 for article in articles if article.get('image'))
                st.metric("With Images", articles_with_images)
            
            with col4:
                st.metric("Extraction Time", extraction_time.strftime("%H:%M:%S") if hasattr(extraction_time, 'strftime') else str(extraction_time))
            
            # Display articles table
            st.subheader("📰 Extracted Articles")
            display_articles_table(articles)
            
            # Create visualizations
            create_visualizations(articles)
            
        else:
            st.info("No articles extracted yet. Go to the 'Extract Articles' tab to start extraction.")
    
    with tab3:
        st.header("Export Data")
        
        if 'articles' in st.session_state and st.session_state.articles:
            articles = st.session_state.articles
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export as JSON
                json_data = json.dumps(articles, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Download as JSON",
                    data=json_data,
                    file_name=f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # Export as CSV
                df_export = pd.DataFrame([
                    {
                        "title": article.get("title", ""),
                        "link": article.get("link", ""),
                        "category": article.get("category", ""),
                        "published_at": article.get("published_at", ""),
                        "summary": article.get("summary", ""),
                        "image": article.get("image", "")
                    }
                    for article in articles
                ])
                
                csv_data = df_export.to_csv(index=False)
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_data,
                    file_name=f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Preview export data
            st.subheader("📋 Export Preview")
            st.dataframe(df_export.head(10), use_container_width=True)
            
        else:
            st.info("No data to export. Extract articles first.")

if __name__ == "__main__":
    main()
