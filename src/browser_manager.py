"""
Browser Manager for Tinder Scraper
Handles browser initialization and management.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages browser initialization and configuration."""
    
    def __init__(self, config):
        """
        Initialize BrowserManager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.driver = None
    
    def setup_browser(self) -> webdriver.Chrome:
        """
        Set up and return a configured Chrome browser instance.
        
        Returns:
            Configured Chrome WebDriver instance
        """
        options = self._get_chrome_options()
        
        try:
            # Try different driver installation methods
            driver = self._try_driver_installations(options)
            
            # Configure the driver
            self._configure_driver(driver)
            
            self.driver = driver
            logger.info("Browser setup completed successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            raise RuntimeError(f"Could not initialize browser: {e}")
    
    def _get_chrome_options(self) -> webdriver.ChromeOptions:
        """Get configured Chrome options."""
        options = webdriver.ChromeOptions()
        
        # Window configuration
        if self.config.get("browser.window_size") == "maximized":
            options.add_argument("--start-maximized")
        else:
            size = self.config.get("browser.window_size", "1920,1080")
            options.add_argument(f"--window-size={size}")
        
        # Headless mode
        if self.config.get("browser.headless", False):
            options.add_argument("--headless")
        
        # Anti-detection options
        if self.config.get("browser.disable_automation_flags", True):
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
        
        # Additional stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        
        logger.debug("Chrome options configured")
        return options
    
    def _try_driver_installations(self, options: webdriver.ChromeOptions) -> webdriver.Chrome:
        """Try different methods to install and initialize ChromeDriver."""
        
        # Method 1: Try with Chromium driver
        try:
            logger.info("Attempting to use Chromium driver...")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("Successfully initialized with Chromium driver")
            return driver
        except Exception as e:
            logger.warning(f"Chromium driver failed: {e}")
        
        # Method 2: Try with Google Chrome driver
        try:
            logger.info("Attempting to use Google Chrome driver...")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("Successfully initialized with Google Chrome driver")
            return driver
        except Exception as e:
            logger.warning(f"Google Chrome driver failed: {e}")
        
        # Method 3: Try with undetected-chromedriver
        try:
            logger.info("Attempting to use undetected-chromedriver...")
            driver = uc.Chrome(options=options)
            logger.info("Successfully initialized with undetected-chromedriver")
            return driver
        except Exception as e:
            logger.warning(f"Undetected-chromedriver failed: {e}")
        
        # Method 4: Try default ChromeDriverManager
        try:
            logger.info("Attempting to use default ChromeDriverManager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("Successfully initialized with default ChromeDriverManager")
            return driver
        except Exception as e:
            logger.error(f"All driver installation methods failed. Last error: {e}")
            raise
    
    def _configure_driver(self, driver: webdriver.Chrome) -> None:
        """Configure the driver with stealth settings."""
        
        # Add stealth JavaScript to avoid detection
        stealth_js = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Remove automation indicators
        delete window.chrome.runtime.onConnect;
        delete window.chrome.runtime.onMessage;
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        """
        
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": stealth_js
            })
            logger.debug("Stealth configuration applied")
        except Exception as e:
            logger.warning(f"Could not apply stealth configuration: {e}")
        
        # Set timeouts
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        logger.debug("Driver configuration completed")
    
    def navigate_to_tinder(self) -> None:
        """Navigate to Tinder and wait for manual login."""
        if not self.driver:
            raise RuntimeError("Browser not initialized. Call setup_browser() first.")
        
        logger.info("Navigating to Tinder...")
        self.driver.get("https://tinder.com/")
        
        # Wait for page to load
        time.sleep(self.config.get("delays.page_load", 10))
        
        # Prompt for manual login
        logger.info("Please log in to Tinder manually...")
        input("🔑 Log in to Tinder manually and press ENTER to continue... ")
        
        logger.info("✅ Ready to start scraping")
    
    def close_popups(self) -> None:
        """Close any popup windows or modals."""
        if not self.driver:
            return
        
        popup_selectors = [
            '//*[@id="c478825258"]/div/div/div[1]/div/div[3]/button',
            "//button[@title='Volver a intentarlo' or .//span[text()='Cerrar']]",
            "//img[contains(@src, 'https://tinder.com/static/build')]",
            "//span[text()='VAMOS ALLÁ']/ancestor::button",
            "//div[contains(text(), 'No me interesa')]",
            "//div[@class='lxn9zzn' and contains(text(), 'No, gracias')]",
            "//div[contains(text(), 'No, gracias')]"
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
    
    def refresh_page(self) -> None:
        """Refresh the current page and wait for it to load."""
        if not self.driver:
            return
        
        logger.info("Refreshing page...")
        self.driver.refresh()
        time.sleep(self.config.get("delays.page_load", 10))
    
    def navigate_to_recommendations(self) -> None:
        """Navigate to the Tinder recommendations page."""
        if not self.driver:
            return
        
        logger.info("Navigating to recommendations page...")
        self.driver.get("https://tinder.com/app/recs")
        time.sleep(self.config.get("delays.page_load", 10))
    
    def quit(self) -> None:
        """Close the browser."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None