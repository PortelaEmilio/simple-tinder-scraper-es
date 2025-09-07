"""
OCR Processor for Tinder Scraper
Handles OCR text extraction and verification icon detection.
"""

import cv2
import pytesseract
import numpy as np
import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR operations and verification detection."""
    
    def __init__(self, config):
        """
        Initialize OCRProcessor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.tesseract_config = config.get("ocr.tesseract_config", "--oem 3 --psm 6")
        self.verification_threshold = config.get("ocr.verification_threshold", 0.75)
        self.verification_template_path = config.get("paths.verification_template", "templates/tick_icon.png")
    
    def extract_text_from_image(self, image_path: str) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (has_text: bool, image: np.ndarray or None)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not open image: {image_path}")
                return False, None
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            logger.debug(f"OCR raw text: {repr(text)}")
            
            # Check if any meaningful text was detected
            has_text = self._has_meaningful_text(text)
            
            if has_text:
                logger.debug("✅ OCR detected meaningful text")
            else:
                logger.debug("❌ OCR did not detect meaningful text")
            
            return has_text, image
            
        except Exception as e:
            logger.error(f"Error in OCR processing: {e}")
            return False, None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Increase resolution for better OCR
        image_resized = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def _has_meaningful_text(self, text: str) -> bool:
        """
        Check if the OCR text contains meaningful content.
        
        Args:
            text: Text extracted by OCR
            
        Returns:
            True if meaningful text is detected
        """
        import re
        
        # Check for any alphanumeric characters or common punctuation
        meaningful_pattern = r'[A-Za-zÀ-ÿ0-9\.]'
        return bool(re.search(meaningful_pattern, text))
    
    def detect_verification_icon(self, image: np.ndarray) -> str:
        """
        Detect if a verification icon is present in the image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            "Yes" if verified, "No" if not verified, "NA" if error
        """
        if not os.path.exists(self.verification_template_path):
            logger.warning(f"Verification template not found: {self.verification_template_path}")
            self._create_template_directory()
            return "NA"
        
        try:
            template = cv2.imread(self.verification_template_path)
            if template is None:
                logger.warning(f"Could not load verification template: {self.verification_template_path}")
                return "NA"
            
            # Convert both images to grayscale
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Perform template matching
            result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= self.verification_threshold)
            
            is_verified = "Yes" if len(locations[0]) > 0 else "No"
            logger.debug(f"🔍 Profile verification: {is_verified}")
            
            return is_verified
            
        except Exception as e:
            logger.error(f"Error in verification detection: {e}")
            return "NA"
    
    def _create_template_directory(self) -> None:
        """Create template directory and warn about missing template."""
        template_dir = os.path.dirname(self.verification_template_path)
        os.makedirs(template_dir, exist_ok=True)
        
        logger.warning(f"⚠️ Template directory created: {template_dir}")
        logger.warning(f"⚠️ Please add a verification icon image to: {self.verification_template_path}")
    
    def verify_profile_with_ocr(self, image_path: str, selenium_name: str, max_attempts: int = 3) -> Tuple[bool, str]:
        """
        Verify profile using OCR with multiple attempts.
        
        Args:
            image_path: Path to the profile screenshot
            selenium_name: Name extracted by Selenium
            max_attempts: Maximum number of verification attempts
            
        Returns:
            Tuple of (verification_success: bool, verification_status: str)
        """
        verification_status = "NA"
        
        for attempt in range(max_attempts):
            logger.info(f"OCR verification attempt {attempt + 1}/{max_attempts}")
            
            # Extract text and get image for verification detection
            has_text, image = self.extract_text_from_image(image_path)
            
            # Check for verification icon (only on first attempt or if not detected yet)
            if verification_status == "NA" and image is not None:
                verification_status = self.detect_verification_icon(image)
            
            logger.info(f"📊 Selenium name: '{selenium_name}'")
            logger.info(f"✓ Profile verified: {verification_status}")
            
            if has_text:
                logger.info("✅ OCR verification successful")
                # Clean up image after successful verification if configured
                if self.config.get("output.clean_screenshots_after_verification", True):
                    self._cleanup_image(image_path)
                return True, verification_status
            
            if attempt < max_attempts - 1:
                logger.info("⚠️ OCR verification failed, retrying...")
        
        logger.warning("❌ OCR verification failed after all attempts")
        # Clean up image after failed verification
        self._cleanup_image(image_path)
        return False, verification_status
    
    def _cleanup_image(self, image_path: str) -> None:
        """
        Remove image file if configured to do so.
        
        Args:
            image_path: Path to the image file to remove
        """
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.debug(f"Cleaned up image: {image_path}")
        except Exception as e:
            logger.warning(f"Could not remove image {image_path}: {e}")
    
    def check_tesseract_installation(self) -> bool:
        """
        Check if Tesseract is properly installed.
        
        Returns:
            True if Tesseract is available
        """
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            return True
        except Exception as e:
            logger.error(f"Tesseract not found or not properly installed: {e}")
            logger.error("Please install Tesseract OCR:")
            logger.error("- Ubuntu/Debian: sudo apt install tesseract-ocr")
            logger.error("- macOS: brew install tesseract")
            logger.error("- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            return False