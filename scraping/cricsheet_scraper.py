from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import time

# Create the folder to store downloaded JSONs
DOWNLOAD_FOLDER = "data/json"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Setup Chrome options
options = Options()
options.add_argument('--headless')  # Run in headless mode (invisible browser)
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Launch browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

try:
    # Step 1: Go to Cricsheet match list page
    driver.get("https://cricsheet.org/matches/")
    time.sleep(2)

    print(" Searching for match links...")
    # Scroll down to load the table
    # Scroll to load full table
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

#  FIXED SELECTOR
    wait.until(EC.presence_of_element_located((By.XPATH, '//table//a[contains(@href, "/matches/")]')))

# Extract match links
    match_links = driver.find_elements(By.XPATH, '//table//a[contains(@href, "/matches/")]')

    print(f"🔗 Found {len(match_links)} match pages...")


    downloaded_count = 0

    # Step 3: Loop through each match page
    for url in match_urls[:10]:  # Limit to first 10 for demo/testing
        try:
            driver.get(url)
            time.sleep(2)

            # Step 4: Locate the JSON download link using dynamic XPath
            json_link_element = driver.find_element(
                By.XPATH,
                '//a[contains(@href, "/downloads/json/") and contains(@href, ".json")]'
            )
            json_url = json_link_element.get_attribute("href")

            # Add base URL if it's a relative link
            if json_url.startswith("/"):
                json_url = "https://cricsheet.org" + json_url

            # Step 5: Download and save the JSON file
            match_id = url.split("/")[-1].replace(".html", "")
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{match_id}.json")

            response = requests.get(json_url)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f" Downloaded: {match_id}.json")
                downloaded_count += 1
            else:
                print(f" Failed to download JSON for: {match_id}")

        except Exception as e:
            print(f" Skipped {url}: {str(e)}")

    print(f"\n Download complete. Total files downloaded: {downloaded_count}")

finally:
    driver.quit()
    print("🧹 WebDriver closed.")
