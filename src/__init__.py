"""
Simple Tinder Scraper ES Package
Una herramienta modular para extraer perfiles de Tinder con fines de investigación.
"""

from .scraper import TinderScraper
from .config_manager import ConfigManager
from .browser_manager import BrowserManager
from .ocr_processor import OCRProcessor
from .data_extractor import DataExtractor
from .utils import ScrapingStats, ProfileSaver, setup_logging, validate_dependencies

__version__ = "1.0.0"
__author__ = "Emilio Portela"
__email__ = "portela.emilio@usal.es"

__all__ = [
    "TinderScraper",
    "ConfigManager", 
    "BrowserManager",
    "OCRProcessor",
    "DataExtractor",
    "ScrapingStats",
    "ProfileSaver",
    "setup_logging",
    "validate_dependencies"
]
