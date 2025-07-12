from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import time
import zipfile

# Set up folders
DOWNLOAD_FOLDER = "data/zips"
EXTRACT_FOLDER = "data/json"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

# Set up headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Launch browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Open Cricsheet matches page
    driver.get("https://cricsheet.org/matches/")
    time.sleep(2)

    print("Page loaded. Looking for required match formats...")

    # Find all <dt> elements (match types)
    dt_elements = driver.find_elements(By.XPATH, '//dl/dt')

    download_count = 0

    for dt in dt_elements:
        match_type = dt.text.strip()

       
        if (
            "t20" in match_type.lower() or 
            match_type in ['Test matches', 'One-day internationals', 'Indian Premier League']
        ):
            print(f"✅ Found: {match_type}")
            
            # Get the next sibling <dd>
            dd_element = dt.find_element(By.XPATH, 'following-sibling::dd[1]')
            
            # Find the JSON ZIP link
            json_link_element = dd_element.find_element(By.XPATH, './/a[contains(@href, "_json.zip")]')
            json_url = json_link_element.get_attribute("href")
            file_name = json_url.split("/")[-1]
            file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

            #Download the ZIP file
            print(f"Downloading {file_name}...")
            response = requests.get(json_url)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"Saved: {file_path}")

                #UNZIP the file
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(EXTRACT_FOLDER)
                print(f"Extracted JSONs to: {EXTRACT_FOLDER}")

                #DELETE the ZIP file
                os.remove(file_path)
                print(f"Deleted ZIP: {file_path}")

                download_count += 1
            else:
                print(f"Failed to download {file_name} (status {response.status_code})")

    print(f"\n-----Downloaded and extracted {download_count} JSON ZIP files.")

finally:
    driver.quit()
    print("WebDriver closed.")
