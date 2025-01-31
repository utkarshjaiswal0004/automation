import sys
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import chromedriver_autoinstaller

# Setup logging
logging.basicConfig(level=logging.INFO)

# Automatically install the ChromeDriver
chromedriver_autoinstaller.install()

# Configure WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--no-sandbox")  # Avoid using the sandbox
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

def log_image_urls():
    """Find and return image URLs from the page as JSON."""
    try:
        body_div_locator = (By.CSS_SELECTOR, 'body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1)')

        # Retry mechanism for locating the body div
        for attempt in range(3):
            try:
                body_div = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(body_div_locator)
                )
                break
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed to locate body div: {e}")
                time.sleep(2)
        else:
            logging.error("Failed to locate body div after multiple attempts.")
            return {}

        # Find all image elements
        image_elements = WebDriverWait(body_div, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'img'))
        )

        # Prepare image URLs
        image_urls = [img.get_attribute('src') for img in image_elements if img.get_attribute('src')]

        # Write the image URLs to a JSON file
        with open('image_urls.json', 'w') as f:
            json.dump(image_urls, f)
        
        return image_urls
    
    except Exception as e:
        logging.error(f"Error finding image URLs: {e}")
        return {}

def save_default_info(measurements):
    """Save measurement information in localStorage."""
    try:
        driver.get('https://fittingroom-v3.style.me/')
        js_script = f"""
              const measurements = {json.dumps(measurements)};
              localStorage.setItem('styleme_measurement', JSON.stringify(measurements));
               """
        driver.execute_script(js_script)
    except Exception as e:
        logging.error(f"An error occurred while saving measurements: {e}")

if __name__ == "__main__":
    # Read JSON data passed as a command-line argument
    if len(sys.argv) != 2:
        logging.error("Usage: python selenium_script.py <json_data>")
        sys.exit(1)

    json_data_str = sys.argv[1]
    try:
        measurements = json.loads(json_data_str)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON data: {e}")
        sys.exit(1)

    try:
        save_default_info(measurements)
        driver.get('https://demo.style.me/')

        open_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.style-me-open-button'))
        )
        open_button.click()

        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.style-me-fittingroom'))
        )
        driver.switch_to.frame(iframe)

        # Allow time for the iframe content to load
        time.sleep(5)

        image_urls = log_image_urls()
        logging.info(f"Image URLs found: {image_urls}")
    
    finally:
        logging.info('Exiting...')
        driver.quit()
