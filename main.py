from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

# Path to your ChromeDriver executable
chrome_driver_path = '/Users/utkarshjaiswal/Desktop/techonpixel/projects/Stitch/automation/chromedriver/chromedriver'

# Configure WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--no-sandbox")  # Avoid using the sandbox

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

def log_image_urls():
    """Find and log image URLs from the page."""
    try:
        body_div_locator = (By.CSS_SELECTOR, 'body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1)')

        # Retry mechanism for locating the body div
        for _ in range(3):
            try:
                body_div = WebDriverWait(driver, 4).until(
                    EC.presence_of_element_located(body_div_locator)
                )
                break
            except Exception as e:
                print(f"Error locating body div: {e}")
                time.sleep(2)
        else:
            print("Failed to locate the body div after retries.")
            return

        # Find all image elements
        image_elements = WebDriverWait(body_div, 4).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'img'))
        )

        # Prepare image URLs
        image_urls = [img.get_attribute('src') for img in image_elements if img.get_attribute('src')]

        # Log URLs as JSON
        json_file_path = 'image_urls.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(image_urls, json_file, indent=4)

        print(f"Logged {len(image_urls)} image URLs to {json_file_path}.")

    except Exception as e:
        print(f"An error occurred: {e}")

def save_default_info():
    """Save default measurement information in localStorage."""
    try:
        driver.get('https://fittingroom-v3.style.me/')
        js_script = """
              const measurements = {
            female: {
                height: parseInt(arguments[0]),
                weight: parseInt(arguments[1]),
                waist: 81,
                hip: 97,
                bra: 36,
                underbust: 75,
                bust: 96,
                braCup: "C",
                bellyCurve: 0,
                bodyShape: 3,
                inseam: 72
                  },
                  male: {
                chest: 102,
                height: 183,
                hip: 97,
                waist: 81,
                weight: 77
                  }
              };
              localStorage.setItem('styleme_measurement', JSON.stringify(measurements));
               """
        driver.execute_script(js_script, '170', '65')  # Example height and weight
        print("Measurement data saved in localStorage.")
    except Exception as e:
        print(f"An error occurred: {e}")

try:
    save_default_info()
    driver.get('https://demo.style.me/')

    open_button = WebDriverWait(driver, 4).until(
                   EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.style-me-open-button'))
    )
    open_button.click()

    iframe = WebDriverWait(driver, 4).until(
                   EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.style-me-fittingroom'))
    )
    driver.switch_to.frame(iframe)

    # Allow time for the iframe content to load, if needed
    time.sleep(2)

    log_image_urls()
  
finally:
    print('Exiting...')
    driver.quit()




      # Save data in localStorage
        #   height: 150 - 193,
        #         weight: 49 - 122,
        #         waist: 64 - 90,
        #         hip: 90 - 113,
        #         bra: 30 - 42 (gap - 2),
        #         underbust: 75, (constant)
        #         bust: 96,
        #         braCup: AA, A - F (in capital string),
        #         bellyCurve: 0, (0,1,2)
        #         bodyShape: 3, (0 - 4)
        #         inseam: 74 - 84