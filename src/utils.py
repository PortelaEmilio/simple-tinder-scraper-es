"""
Utilities for Tinder Scraper
Common utility functions and classes.
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

class ScrapingStats:
    """Tracks and displays scraping statistics."""
    
    def __init__(self):
        """Initialize statistics tracking."""
        self.start_time = datetime.now()
        self.profiles_scraped = 0
        self.likes = 0
        self.nopes = 0
        self.errors = 0
        self.last_update = time.time()
    
    def add_profile(self) -> None:
        """Increment profiles scraped counter."""
        self.profiles_scraped += 1
        self.last_update = time.time()
    
    def add_like(self) -> None:
        """Increment likes counter."""
        self.likes += 1
    
    def add_nope(self) -> None:
        """Increment nopes counter."""
        self.nopes += 1
    
    def add_error(self) -> None:
        """Increment errors counter."""
        self.errors += 1
    
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time."""
        elapsed = datetime.now() - self.start_time
        return str(timedelta(seconds=int(elapsed.total_seconds())))
    
    def get_rate(self) -> float:
        """Get profiles per minute rate."""
        elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        if elapsed_minutes > 0:
            return self.profiles_scraped / elapsed_minutes
        return 0.0
    
    def print_stats(self, clear_screen: bool = True) -> None:
        """Print current statistics."""
        if clear_screen:
            os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 60)
        print("🔍 TINDER SCRAPER STATISTICS")
        print("=" * 60)
        print(f"🕒 Time elapsed: {self.get_elapsed_time()}")
        print(f"👥 Profiles scraped: {self.profiles_scraped}")
        print(f"💚 Likes given: {self.likes}")
        print(f"❌ Nopes given: {self.nopes}")
        print(f"⚠️ Errors encountered: {self.errors}")
        print(f"📊 Rate: {self.get_rate():.1f} profiles/min")
        print("=" * 60)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "elapsed_time": self.get_elapsed_time(),
            "profiles_scraped": self.profiles_scraped,
            "likes": self.likes,
            "nopes": self.nopes,
            "errors": self.errors,
            "rate_per_minute": self.get_rate()
        }

class ProfileSaver:
    """Handles saving profiles to JSON files."""
    
    def __init__(self, config):
        """
        Initialize ProfileSaver.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = config.get("output.output_directory", "output")
        self.filename = config.get("output.filename", "profiles.json")
        self.filepath = os.path.join(self.output_dir, self.filename)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_profiles(self, new_profiles: List[Dict[str, Any]]) -> bool:
        """
        Save new profiles to JSON file.
        
        Args:
            new_profiles: List of profile dictionaries to save
            
        Returns:
            True if save was successful
        """
        try:
            # Clean profiles before saving
            cleaned_profiles = self._clean_profiles(new_profiles)
            
            # Load existing profiles
            existing_profiles = self._load_existing_profiles()
            
            # Add new profiles
            existing_profiles.extend(cleaned_profiles)
            
            # Save all profiles
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_profiles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved {len(cleaned_profiles)} profiles. Total: {len(existing_profiles)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving profiles: {e}")
            return False
    
    def _clean_profiles(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and validate profile data.
        
        Args:
            profiles: List of raw profile dictionaries
            
        Returns:
            List of cleaned profile dictionaries
        """
        cleaned_profiles = []
        
        for profile in profiles:
            cleaned_profile = {}
            
            for key, value in profile.items():
                # Handle WebElement objects
                if hasattr(value, 'text'):
                    cleaned_profile[key] = value.text.strip()
                # Handle lists
                elif isinstance(value, list):
                    if value:
                        # Convert all items to strings and join
                        cleaned_profile[key] = " | ".join([str(item) for item in value])
                    else:
                        cleaned_profile[key] = "NA"
                # Handle other types
                else:
                    cleaned_profile[key] = value if value is not None else "NA"
            
            # Ensure specific fields are properly formatted
            self._format_list_fields(cleaned_profile)
            
            cleaned_profiles.append(cleaned_profile)
        
        return cleaned_profiles
    
    def _format_list_fields(self, profile: Dict[str, Any]) -> None:
        """
        Format fields that should be pipe-separated strings.
        
        Args:
            profile: Profile dictionary to modify in place
        """
        list_fields = [
            "intereses", "otros", "horoscopo", "educacion", "hijos",
            "vacunacion", "personalidad", "comunicacion", "amor"
        ]
        
        for field in list_fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, list):
                    if value:
                        profile[field] = " | ".join([str(item) for item in value])
                    else:
                        profile[field] = "NA"
    
    def _load_existing_profiles(self) -> List[Dict[str, Any]]:
        """
        Load existing profiles from file.
        
        Returns:
            List of existing profiles
        """
        if not os.path.exists(self.filepath):
            return []
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                existing_profiles = json.load(f)
                
            if not isinstance(existing_profiles, list):
                logger.warning("Existing profiles file is not a list, starting fresh")
                return []
                
            return existing_profiles
            
        except json.JSONDecodeError:
            logger.warning("Could not parse existing profiles file, starting fresh")
            return []
        except Exception as e:
            logger.error(f"Error loading existing profiles: {e}")
            return []
    
    def get_profile_count(self) -> int:
        """
        Get the number of profiles currently saved.
        
        Returns:
            Number of saved profiles
        """
        existing_profiles = self._load_existing_profiles()
        return len(existing_profiles)

def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("scraper.log", encoding='utf-8')
        ]
    )

def random_delay(min_delay: float, max_delay: float) -> None:
    """
    Sleep for a random amount of time between min and max delay.
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def validate_dependencies() -> bool:
    """
    Validate that all required dependencies are available.
    
    Returns:
        True if all dependencies are available
    """
    missing_deps = []
    
    # Check Python modules
    required_modules = [
        'selenium', 'cv2', 'pytesseract', 'numpy', 'undetected_chromedriver'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    # Check Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except Exception:
        missing_deps.append('tesseract-ocr')
    
    if missing_deps:
        logger.error("Missing dependencies:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        logger.error("\nPlease install missing dependencies:")
        logger.error("pip install -r requirements.txt")
        if 'tesseract-ocr' in missing_deps:
            logger.error("\nFor Tesseract OCR:")
            logger.error("- Ubuntu/Debian: sudo apt install tesseract-ocr")
            logger.error("- macOS: brew install tesseract")
            logger.error("- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    return True

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def create_backup(filepath: str) -> bool:
    """
    Create a backup of a file.
    
    Args:
        filepath: Path to the file to backup
        
    Returns:
        True if backup was successful
    """
    if not os.path.exists(filepath):
        return True
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{filepath}.backup_{timestamp}"
        
        import shutil
        shutil.copy2(filepath, backup_path)
        
        logger.info(f"Backup created: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False