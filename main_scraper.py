#!/usr/bin/env python3
"""
SMM Silver Price Scraper
Scrapes silver price data from metal.com and saves to CSV with screenshots
"""

import os
import csv
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SMMSilverScraper:
    def __init__(self):
        self.url = "https://metal.com/Silver/20110225392"
        self.csv_folder = "csv"
        self.screenshot_folder = "screenshots"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for folder in [self.csv_folder, self.screenshot_folder, 'logs']:
            os.makedirs(folder, exist_ok=True)
            
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Remove this line if you want to see the browser
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Install ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
        
    def extract_data(self, driver):
        """Extract date and price data from the page"""
        try:
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            
            # Extract date - look for the date element
            date_element = wait.until(EC.presence_of_element_located((By.XPATH, "//time | //div[contains(@class, 'date')] | //span[contains(text(), '2025')]")))
            date_text = date_element.text.strip()
            logger.info(f"Found date text: {date_text}")
            
            # Extract price - look for the original price (CNY/kg)
            price_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'price')] | //span[contains(text(), 'CNY/kg')] | //div[contains(text(), 'CNY/kg')]")
            
            original_price = None
            for element in price_elements:
                text = element.text.strip()
                if 'CNY/kg' in text and any(char.isdigit() for char in text):
                    # Extract numeric value from text like "9,351 CNY/kg"
                    import re
                    price_match = re.search(r'([\d,]+)\s*CNY/kg', text)
                    if price_match:
                        original_price = price_match.group(1).replace(',', '')
                        logger.info(f"Found original price: {original_price}")
                        break
            
            # If specific elements not found, try alternative selectors
            if not original_price:
                # Try to find any element with the price pattern
                all_text = driver.find_element(By.TAG_NAME, "body").text
                import re
                price_matches = re.findall(r'([\d,]+)\s*CNY/kg', all_text)
                if price_matches:
                    original_price = price_matches[0].replace(',', '')
                    logger.info(f"Found price via text search: {original_price}")
            
            # Parse date to Python-friendly format
            parsed_date = self.parse_date(date_text)
            
            return {
                'date': parsed_date,
                'rate': original_price,
                'raw_date': date_text
            }
            
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            # Fallback: try to extract from page source
            return self.extract_fallback_data(driver)
    
    def extract_fallback_data(self, driver):
        """Fallback method to extract data from page source"""
        try:
            page_source = driver.page_source
            import re
            
            # Look for date patterns
            date_patterns = [
                r'Jul\s+\d+,\s+2025',
                r'\d{4}-\d{2}-\d{2}',
                r'\d{2}/\d{2}/2025'
            ]
            
            found_date = None
            for pattern in date_patterns:
                match = re.search(pattern, page_source)
                if match:
                    found_date = match.group()
                    break
            
            # Look for price patterns
            price_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*CNY/kg',
                r'(\d+,\d+)\s*CNY',
                r'>(\d{1,3}(?:,\d{3})*)<.*?CNY'
            ]
            
            found_price = None
            for pattern in price_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    found_price = matches[0].replace(',', '') if isinstance(matches[0], str) else str(matches[0]).replace(',', '')
                    break
            
            parsed_date = self.parse_date(found_date) if found_date else datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Fallback extraction - Date: {found_date}, Price: {found_price}")
            
            return {
                'date': parsed_date,
                'rate': found_price,
                'raw_date': found_date
            }
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {str(e)}")
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'rate': None,
                'raw_date': 'Error'
            }
    
    def parse_date(self, date_text):
        """Parse various date formats to YYYY-MM-DD format"""
        if not date_text:
            return datetime.now().strftime('%Y-%m-%d')
            
        try:
            # Handle "Jul 24, 2025" format
            if ',' in date_text and any(month in date_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                parsed = datetime.strptime(date_text, '%b %d, %Y')
                return parsed.strftime('%Y-%m-%d')
            
            # Handle other common formats
            date_formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%d-%m-%Y',
                '%B %d, %Y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed = datetime.strptime(date_text, fmt)
                    return parsed.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.error(f"Date parsing error: {str(e)}")
            
        return datetime.now().strftime('%Y-%m-%d')
    
    def take_screenshot(self, driver, data):
        """Take screenshot of the page highlighting the data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(self.screenshot_folder, f'smm_silver_{timestamp}.png')
            
            # Take full page screenshot
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Screenshot error: {str(e)}")
            return None
    
    def save_to_csv(self, data):
        """Save extracted data to CSV file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d')
            csv_path = os.path.join(self.csv_folder, f'smm_silver_prices_{timestamp}.csv')
            
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(csv_path)
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as file:
                fieldnames = ['timestamp', 'date', 'rate', 'raw_date', 'scrape_time']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                # Add scrape timestamp
                data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data['scrape_time'] = datetime.now().strftime('%H:%M:%S')
                
                writer.writerow(data)
                logger.info(f"Data saved to CSV: {csv_path}")
                
            return csv_path
            
        except Exception as e:
            logger.error(f"CSV save error: {str(e)}")
            return None
    
    def run_scraper(self):
        """Main method to run the scraper"""
        logger.info("Starting SMM Silver Price Scraper")
        driver = None
        
        try:
            # Setup WebDriver
            driver = self.setup_driver()
            logger.info("WebDriver initialized")
            
            # Navigate to the page
            logger.info(f"Navigating to: {self.url}")
            driver.get(self.url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Extract data
            logger.info("Extracting data...")
            data = self.extract_data(driver)
            
            if data['rate']:
                logger.info(f"Successfully extracted - Date: {data['date']}, Rate: {data['rate']}")
                
                # Take screenshot
                screenshot_path = self.take_screenshot(driver, data)
                
                # Save to CSV
                csv_path = self.save_to_csv(data)
                
                logger.info("Scraping completed successfully")
                return True
            else:
                logger.warning("No price data extracted")
                return False
                
        except Exception as e:
            logger.error(f"Scraper error: {str(e)}")
            return False
            
        finally:
            if driver:
                driver.quit()
                logger.info("WebDriver closed")

def main():
    """Main function"""
    scraper = SMMSilverScraper()
    success = scraper.run_scraper()
    
    if success:
        print("✅ Scraping completed successfully!")
    else:
        print("❌ Scraping failed. Check logs for details.")

if __name__ == "__main__":
    main()
