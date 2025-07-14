"""
Web Scraper Configuration Manager
Handles loading and validation of configuration settings.
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path


class Config:
    """Configuration manager for web scraper settings."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    @classmethod
    def from_dict(cls, config_data: Dict[str, Any]) -> 'Config':
        """
        Create Config instance from dictionary without file loading.
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            Config instance
        """
        instance = cls.__new__(cls)
        instance.config_path = None
        instance.config = config_data
        # Skip validation for flexibility in Streamlit app
        return instance
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.example.json to {self.config_path}"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _validate_config(self) -> None:
        """Validate required configuration fields."""
        required_fields = [
            'base_url', 'max_articles', 'crawl_delay', 
            'output_formats', 'user_agent', 'selectors'
        ]
        
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Required configuration field missing: {field}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def get_selectors(self) -> Dict[str, str]:
        """Get CSS selectors configuration."""
        return self.config.get('selectors', {})
    
    def get_output_directory(self) -> Path:
        """Get output directory path."""
        output_dir = Path(self.config.get('output_directory', './output'))
        output_dir.mkdir(exist_ok=True)
        return output_dir
