"""
Data Extractor for Tinder Scraper
Handles extraction of profile data from Tinder pages.
"""

import time
import re
import os
import logging
from datetime import datetime
from typing import Dict, List, Set, Any, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

class DataExtractor:
    """Handles extraction of profile data from Tinder pages."""
    
    def __init__(self, driver, config, ocr_processor):
        """
        Initialize DataExtractor.
        
        Args:
            driver: Selenium WebDriver instance
            config: Configuration dictionary
            ocr_processor: OCRProcessor instance
        """
        self.driver = driver
        self.config = config
        self.ocr_processor = ocr_processor
        self.screenshots_dir = config.get("paths.screenshots_dir", "screenshots")
        
        # Ensure screenshots directory exists
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def extract_profile_data(self) -> Optional[Dict[str, Any]]:
        """
        Extract complete profile data from current Tinder profile.
        
        Returns:
            Dictionary containing all extracted profile data, or None if extraction fails
        """
        max_retries = self.config.get("scraping.max_retries", 3)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Profile extraction attempt {attempt + 1}/{max_retries}")
                
                # Handle popups and navigation
                if not self._prepare_profile_page():
                    continue
                
                # Extract basic profile information
                name, age = self._extract_basic_info()
                if not name:
                    logger.warning("Could not extract profile name, skipping...")
                    continue
                
                # Take screenshot and verify with OCR
                profile_id, screenshot_path = self._take_profile_screenshot(name)
                if not screenshot_path:
                    continue
                
                # Verify profile with OCR
                ocr_verified, verification_status = self.ocr_processor.verify_profile_with_ocr(
                    screenshot_path, name, max_attempts=self.config.get("ocr.max_attempts", 3)
                )
                
                if not ocr_verified:
                    logger.warning("OCR verification failed, retrying...")
                    self._refresh_and_wait()
                    continue
                
                # Extract all profile data
                profile_data = self._extract_all_profile_data(profile_id, name, age, verification_status)
                
                logger.info(f"✅ Successfully extracted profile: {name}")
                return profile_data
                
            except Exception as e:
                logger.error(f"Error in profile extraction attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error("Failed to extract profile after all attempts")
                    return None
                time.sleep(1)
        
        return None
    
    def _prepare_profile_page(self) -> bool:
        """
        Prepare the profile page for data extraction.
        
        Returns:
            True if page is ready, False otherwise
        """
        try:
            # Close any popups
            self._close_popups()
            
            # Navigate profile with arrow keys
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
            time.sleep(self.config.get("delays.screenshot_wait", 0.4))
            
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_UP)
            time.sleep(self.config.get("delays.screenshot_wait", 0.4))
            
            return True
            
        except Exception as e:
            logger.warning(f"Could not prepare profile page: {e}")
            return False
    
    def _close_popups(self) -> None:
        """Close any popup windows or overlays."""
        popup_selectors = [
            '//*[@id="c478825258"]/div/div/div[1]/div/div[3]/button',
            "//button[@title='Volver a intentarlo' or .//span[text()='Cerrar']]",
            "//img[contains(@src, 'https://tinder.com/static/build')]",
            "//span[text()='VAMOS ALLÁ']/ancestor::button",
            "//div[contains(text(), 'No me interesa')]",
            "//div[@class='lxn9zzn' and contains(text(), 'No, gracias')]"
        ]
        
        for selector in popup_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    element.click()
                    time.sleep(self.config.get("delays.popup_close", 0.2))
                    logger.debug(f"Closed popup with selector: {selector}")
                    break
            except:
                continue
    
    def _extract_basic_info(self) -> Tuple[str, str]:
        """
        Extract basic profile information (name and age).
        
        Returns:
            Tuple of (name, age)
        """
        name = ""
        age = ""
        
        # Try different selectors for name
        name_selectors = [
            "//span[contains(@class, 'Pend(8px)')]",
            "//h1[contains(@aria-label, 'años')]"
        ]
        
        for selector in name_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if selector.endswith("años')]"): 
                    # Extract name from aria-label
                    aria_label = element.get_attribute("aria-label")
                    name = aria_label.split()[0] if aria_label else ""
                else:
                    name = element.text.strip()
                
                if name:
                    break
            except:
                continue
        
        # Try to extract age
        age_selectors = [
            "//span[contains(@class, 'Whs(nw)') and contains(@class, 'Typs(display-2-regular)')]"
        ]
        
        for selector in age_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                age = element.text.strip()
                if age:
                    break
            except:
                continue
        
        logger.debug(f"Extracted basic info - Name: {name}, Age: {age}")
        return name, age
    
    def _take_profile_screenshot(self, name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Take a screenshot of the profile.
        
        Args:
            name: Profile name for filename
            
        Returns:
            Tuple of (profile_id, screenshot_path)
        """
        try:
            # XPath of the profile element to capture
            xpath = "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div/div[1]/div[1]/div[1]/div"
            
            # Find the element
            element = self.driver.find_element(By.XPATH, xpath)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            profile_id = f"{name}_{timestamp}"
            filename = os.path.join(self.screenshots_dir, f"{profile_id}.png")
            
            # Take screenshot of element
            element.screenshot(filename)
            logger.debug(f"📸 Screenshot saved: {filename}")
            
            return profile_id, filename
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None, None
    
    def _extract_all_profile_data(self, profile_id: str, name: str, age: str, verification_status: str) -> Dict[str, Any]:
        """
        Extract all available profile data.
        
        Args:
            profile_id: Unique profile identifier
            name: Profile name
            age: Profile age
            verification_status: Verification status from OCR
            
        Returns:
            Complete profile data dictionary
        """
        # Extract image URLs
        image_urls = self._extract_image_urls()
        
        # Extract detailed profile information
        profile_details = self._extract_profile_details()
        
        # Combine all data
        profile_data = {
            "id": profile_id,
            "nombre": name,
            "edad": age,
            "verificado": verification_status,
            "imagenes": list(image_urls),
            **profile_details
        }
        
        return profile_data
    
    def _extract_image_urls(self) -> Set[str]:
        """
        Extract all image URLs from the profile.
        
        Returns:
            Set of image URLs
        """
        urls_found = set()
        scrolls_without_changes = 0
        max_scrolls = self.config.get("scraping.scroll_attempts", 3)
        
        while scrolls_without_changes < max_scrolls:
            try:
                # Find elements with background-image style
                elements = self.driver.find_elements(By.XPATH, "//*[contains(@style, 'background-image')]")
                new_urls = set()
                
                for element in elements:
                    style = element.get_attribute("style")
                    match = re.search(r'url\("?(https:[^)"]+)"?\)', style)
                    if match:
                        url = match.group(1)
                        # Filter for Tinder image URLs
                        if ".webp" in url and len(url) > 250:
                            new_urls.add(url)
                
                # Check if we found new URLs
                new_urls_in_iteration = new_urls - urls_found
                if new_urls_in_iteration:
                    urls_found.update(new_urls_in_iteration)
                    scrolls_without_changes = 0
                    logger.debug(f"Found {len(new_urls_in_iteration)} new image URLs")
                else:
                    scrolls_without_changes += 1
                
                # Scroll to load more images
                if scrolls_without_changes < max_scrolls:
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error extracting image URLs: {e}")
                break
        
        logger.info(f"Extracted {len(urls_found)} image URLs")
        return urls_found
    
    def _extract_profile_details(self) -> Dict[str, Any]:
        """
        Extract detailed profile information.
        
        Returns:
            Dictionary with detailed profile data
        """
        details = {
            "bio": "NA",
            "busco": "NA",
            "altura": "NA",
            "distancia": "NA",
            "ubicacion": "NA",
            "intereses": [],
            "idiomas": "NA",
            "mascotas": "NA",
            "beber": "NA",
            "fumar": "NA",
            "deporte": "NA",
            "sueño": "NA",
            "redes_sociales": "NA",
            "alimentacion": "NA",
            "orientacion_sexual": "NA",
            "genero": "NA",
            "relacion_tipo": "NA",
            "educacion": "NA",
            "hijos": "NA",
            "vacunacion": "NA",
            "personalidad": "NA",
            "comunicacion": "NA",
            "amor": "NA",
            "horoscopo": "NA",
            "otros": []
        }
        
        try:
            # Extract bio
            details["bio"] = self._extract_bio()
            
            # Extract interests
            details["intereses"] = self._extract_interests()
            
            # Extract other profile fields
            self._extract_additional_fields(details)
            
        except Exception as e:
            logger.warning(f"Error extracting profile details: {e}")
        
        return details
    
    def _extract_bio(self) -> str:
        """Extract profile bio/description."""
        bio_selectors = [
            "//div[contains(@class, 'bio')]//text()",
            "//div[contains(@class, 'description')]",
            "//span[contains(@class, 'description')]"
        ]
        
        for selector in bio_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                bio = element.text.strip()
                if bio:
                    return bio
            except:
                continue
        
        return "NA"
    
    def _extract_interests(self) -> List[str]:
        """Extract profile interests/hobbies."""
        interests = []
        
        # Try different selectors for interests
        interest_selectors = [
            "//div[contains(@class, 'interest')]",
            "//span[contains(@class, 'tag')]",
            "//div[contains(@class, 'hobby')]"
        ]
        
        for selector in interest_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and text not in interests:
                        interests.append(text)
            except:
                continue
        
        return interests
    
    def _extract_additional_fields(self, details: Dict[str, Any]) -> None:
        """Extract additional profile fields."""
        # This is a simplified version - you can expand this based on the specific
        # structure of Tinder profiles and the data you want to extract
        
        try:
            # Extract any additional text elements that might contain profile information
            text_elements = self.driver.find_elements(By.XPATH, "//span | //div")
            
            for element in text_elements:
                try:
                    text = element.text.strip()
                    if text and len(text) < 100:  # Avoid very long texts
                        # You can add specific parsing logic here based on patterns
                        # For example, height, distance, etc.
                        if "km" in text and len(text) < 10:
                            details["distancia"] = text
                        elif "cm" in text and len(text) < 10:
                            details["altura"] = text
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error extracting additional fields: {e}")
    
    def _refresh_and_wait(self) -> None:
        """Refresh the page and wait for it to load."""
        logger.info("Refreshing page...")
        self.driver.refresh()
        time.sleep(self.config.get("delays.page_load", 10))