"""
Main Scraper Module for Tinder Scraper
Coordinates all scraping operations.
"""

import time
import random
import logging
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .browser_manager import BrowserManager
from .ocr_processor import OCRProcessor
from .data_extractor import DataExtractor
from .utils import ScrapingStats, ProfileSaver, random_delay

logger = logging.getLogger(__name__)

class TinderScraper:
    """Main scraper class that coordinates all scraping operations."""
    
    def __init__(self, config):
        """
        Initialize TinderScraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.browser_manager = BrowserManager(config)
        self.ocr_processor = OCRProcessor(config)
        self.profile_saver = ProfileSaver(config)
        self.stats = ScrapingStats()
        
        self.driver = None
        self.data_extractor = None
        
        # Scraping parameters
        self.num_profiles = config.get("scraping.num_profiles", 10)
        self.like_probability = config.get("scraping.like_probability", 0.151)
        self.save_interval = config.get("scraping.save_interval", 10)
        self.timeout_minutes = config.get("scraping.timeout_minutes", 1)
        
        # State tracking
        self.profiles_buffer = []
        self.last_profile_time = time.time()
        self.last_save = 0
    
    def setup(self) -> bool:
        """
        Setup the scraper (browser, OCR, etc.).
        
        Returns:
            True if setup was successful
        """
        try:
            logger.info("🚀 Setting up Tinder Scraper...")
            
            # Check OCR installation
            if not self.ocr_processor.check_tesseract_installation():
                return False
            
            # Setup browser
            self.driver = self.browser_manager.setup_browser()
            
            # Initialize data extractor
            self.data_extractor = DataExtractor(self.driver, self.config, self.ocr_processor)
            
            # Navigate to Tinder and wait for login
            self.browser_manager.navigate_to_tinder()
            
            logger.info("✅ Scraper setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup scraper: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """
        Run the scraping process.
        
        Returns:
            Dictionary with scraping results and statistics
        """
        logger.info(f"🎯 Starting scraping session for {self.num_profiles} profiles")
        
        try:
            for i in range(1, self.num_profiles + 1):
                logger.info(f"\n--- Processing profile {i}/{self.num_profiles} ---")
                
                # Check timeout
                if self._check_timeout():
                    continue
                
                # Extract profile data
                profile_data = self._extract_single_profile()
                
                if profile_data:
                    # Validate profile has images
                    if self._validate_profile(profile_data):
                        self.profiles_buffer.append(profile_data)
                        self.stats.add_profile()
                        self.last_profile_time = time.time()
                        
                        logger.info(f"✅ Profile '{profile_data['nombre']}' added to buffer")
                    else:
                        logger.warning("Profile validation failed, navigating to recommendations...")
                        self.browser_manager.navigate_to_recommendations()
                        continue
                else:
                    self.stats.add_error()
                    logger.warning("Failed to extract profile data")
                
                # Perform swipe action
                self._perform_swipe_action()
                
                # Save profiles periodically
                self._save_if_needed()
                
                # Update statistics
                self.stats.print_stats()
                
                # Random delay between profiles
                delay_range = self.config.get("delays.after_action", [0.2, 0.4])
                random_delay(delay_range[0], delay_range[1])
            
            # Final save
            self._save_remaining_profiles()
            
            # Final statistics
            final_stats = self._get_final_statistics()
            logger.info("🎉 Scraping session completed successfully")
            
            return final_stats
            
        except KeyboardInterrupt:
            logger.info("⚠️ Scraping interrupted by user")
            self._save_remaining_profiles()
            return self._get_final_statistics()
            
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            self._save_remaining_profiles()
            return self._get_final_statistics()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("🧹 Cleaning up...")
        
        if self.browser_manager:
            self.browser_manager.quit()
        
        logger.info("✅ Cleanup completed")
    
    def _check_timeout(self) -> bool:
        """
        Check if too much time has passed without adding a profile.
        
        Returns:
            True if timeout occurred and page was refreshed
        """
        current_time = time.time()
        timeout_seconds = self.timeout_minutes * 60
        
        if current_time - self.last_profile_time > timeout_seconds:
            logger.warning(f"⚠️ Timeout: {self.timeout_minutes} minute(s) without new profile")
            self.browser_manager.navigate_to_recommendations()
            self.last_profile_time = time.time()
            return True
        
        return False
    
    def _extract_single_profile(self) -> Optional[Dict[str, Any]]:
        """
        Extract data from a single profile.
        
        Returns:
            Profile data dictionary or None if extraction failed
        """
        try:
            return self.data_extractor.extract_profile_data()
        except Exception as e:
            logger.error(f"Error extracting profile: {e}")
            return None
    
    def _validate_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Validate that profile data is complete and has images.
        
        Args:
            profile_data: Profile data dictionary
            
        Returns:
            True if profile is valid
        """
        # Check if profile has images
        images = profile_data.get("imagenes", [])
        if not images or images == "NA" or len(images) == 0:
            logger.warning("⚠️ Profile has no images")
            return False
        
        # Check if profile has basic information
        if not profile_data.get("nombre") or profile_data.get("nombre") == "NA":
            logger.warning("⚠️ Profile has no name")
            return False
        
        logger.debug(f"✅ Profile validation passed: {len(images)} images")
        return True
    
    def _perform_swipe_action(self) -> None:
        """Perform a swipe action (like or nope)."""
        try:
            # Determine action based on probability
            action = Keys.ARROW_RIGHT if random.random() < self.like_probability else Keys.ARROW_LEFT
            
            # Perform the action
            self.driver.find_element(By.TAG_NAME, "body").send_keys(action)
            
            # Update statistics
            if action == Keys.ARROW_RIGHT:
                self.stats.add_like()
                logger.debug("💚 Swiped right (like)")
            else:
                self.stats.add_nope()
                logger.debug("❌ Swiped left (nope)")
                
        except Exception as e:
            logger.warning(f"Error performing swipe action: {e}")
            self.stats.add_error()
    
    def _save_if_needed(self) -> None:
        """Save profiles if the save interval has been reached."""
        profiles_to_save = len(self.profiles_buffer) - self.last_save
        
        if profiles_to_save >= self.save_interval:
            profiles_for_save = self.profiles_buffer[self.last_save:]
            
            if self.profile_saver.save_profiles(profiles_for_save):
                self.last_save = len(self.profiles_buffer)
                logger.info(f"💾 Saved {len(profiles_for_save)} profiles to file")
            else:
                logger.error("Failed to save profiles")
    
    def _save_remaining_profiles(self) -> None:
        """Save any remaining profiles in the buffer."""
        remaining_profiles = self.profiles_buffer[self.last_save:]
        
        if remaining_profiles:
            if self.profile_saver.save_profiles(remaining_profiles):
                logger.info(f"💾 Final save: {len(remaining_profiles)} profiles")
            else:
                logger.error("Failed to save remaining profiles")
    
    def _get_final_statistics(self) -> Dict[str, Any]:
        """
        Get final scraping statistics.
        
        Returns:
            Dictionary with final statistics
        """
        total_saved = self.profile_saver.get_profile_count()
        
        final_stats = {
            "session_stats": self.stats.to_dict(),
            "total_profiles_in_file": total_saved,
            "profiles_extracted_this_session": len(self.profiles_buffer),
            "success_rate": (len(self.profiles_buffer) / self.num_profiles * 100) if self.num_profiles > 0 else 0
        }
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📊 FINAL SCRAPING SUMMARY")
        print("=" * 60)
        print(f"⏱️  Session duration: {final_stats['session_stats']['elapsed_time']}")
        print(f"🎯 Target profiles: {self.num_profiles}")
        print(f"✅ Profiles extracted: {final_stats['profiles_extracted_this_session']}")
        print(f"💾 Total profiles saved: {final_stats['total_profiles_in_file']}")
        print(f"📈 Success rate: {final_stats['success_rate']:.1f}%")
        print(f"⚡ Average rate: {final_stats['session_stats']['rate_per_minute']:.1f} profiles/min")
        print("=" * 60)
        
        return final_stats
    
    def get_current_stats(self) -> Dict[str, Any]:
        """
        Get current scraping statistics.
        
        Returns:
            Current statistics dictionary
        """
        return {
            "stats": self.stats.to_dict(),
            "profiles_in_buffer": len(self.profiles_buffer),
            "profiles_saved": self.profile_saver.get_profile_count()
        }