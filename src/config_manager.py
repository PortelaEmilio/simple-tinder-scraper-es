"""
Configuration Manager for Tinder Scraper
Handles loading and validation of configuration files.
"""

import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration loading and validation."""
    
    DEFAULT_CONFIG_PATH = "config/default_config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to custom configuration file
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "scraping": {
                "num_profiles": 10,
                "like_probability": 0.151,
                "save_interval": 10,
                "max_retries": 3,
                "scroll_attempts": 3,
                "timeout_minutes": 1
            },
            "browser": {
                "headless": False,
                "window_size": "maximized",
                "disable_automation_flags": True,
                "chrome_type": "auto"
            },
            "ocr": {
                "max_attempts": 3,
                "verification_threshold": 0.75,
                "tesseract_config": "--oem 3 --psm 6"
            },
            "output": {
                "filename": "profiles.json",
                "save_screenshots": True,
                "clean_screenshots_after_verification": True,
                "output_directory": "output"
            },
            "delays": {
                "after_action": [0.2, 0.4],
                "page_load": 10,
                "popup_close": 0.2,
                "screenshot_wait": 0.4
            },
            "paths": {
                "screenshots_dir": "screenshots",
                "templates_dir": "templates",
                "verification_template": "templates/tick_icon.png"
            }
        }
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        required_sections = ["scraping", "browser", "ocr", "output", "delays", "paths"]
        
        for section in required_sections:
            if section not in self.config:
                logger.warning(f"Missing configuration section: {section}")
                self.config[section] = self._get_default_config()[section]
        
        # Validate numeric values
        self._validate_numeric("scraping.num_profiles", min_val=1, max_val=1000)
        self._validate_numeric("scraping.like_probability", min_val=0.0, max_val=1.0)
        self._validate_numeric("scraping.save_interval", min_val=1, max_val=100)
        self._validate_numeric("ocr.verification_threshold", min_val=0.0, max_val=1.0)
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _validate_numeric(self, key_path: str, min_val: float, max_val: float) -> None:
        """Validate numeric configuration value."""
        try:
            keys = key_path.split('.')
            value = self.config
            for key in keys:
                value = value[key]
            
            if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
                logger.warning(f"Invalid value for {key_path}: {value}. Using default.")
                # Reset to default
                default_config = self._get_default_config()
                default_value = default_config
                for key in keys:
                    default_value = default_value[key]
                
                # Set the default value
                target = self.config
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = default_value
                
        except (KeyError, TypeError):
            logger.warning(f"Missing or invalid configuration key: {key_path}")
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.config["output"]["output_directory"],
            self.config["paths"]["screenshots_dir"],
            self.config["paths"]["templates_dir"]
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration value
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key_path.split('.')
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def update(self, key_path: str, value: Any) -> None:
        """
        Update configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration value
            value: New value to set
        """
        keys = key_path.split('.')
        target = self.config
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
        logger.debug(f"Configuration updated: {key_path} = {value}")
    
    def save(self, output_path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            output_path: Path to save configuration (default: current config path)
        """
        output_path = output_path or self.config_path
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_full_config(self) -> Dict[str, Any]:
        """Return the complete configuration dictionary."""
        return self.config.copy()