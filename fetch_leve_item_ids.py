import os
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'https://universalis.app/'
RESULTS_SELECTOR = 'div.search-results-container.open'
ANCHOR_SELECTOR = 'div.simplebar-content a'
SEARCH_INPUT_SELECTOR = 'input.search'


def get_market_id(driver, item_name, timeout=10):
    """
    Searches Universalis for item_name and returns the market ID (int) or None.
    """
    driver.get(BASE_URL)
    try:
        # Wait for search input to be present
        search_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_SELECTOR))
        )
        search_input.clear()
        search_input.send_keys(item_name)
        search_input.send_keys(Keys.RETURN)

        # Wait for results container
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, RESULTS_SELECTOR))
        )
        # Grab the first result link
        anchor = driver.find_element(By.CSS_SELECTOR, ANCHOR_SELECTOR)
        href = anchor.get_attribute('href')
        match = re.search(r'/market/(\d+)', href)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Error fetching ID for '{item_name}': {e}")
    return None


def main():
    directory = 'Clean Leves'
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return

    # Setup headless Chrome browser
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        for fname in os.listdir(directory):
            if not fname.lower().endswith('.json'):
                continue

            file_path = os.path.join(directory, fname)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
                continue

            updated = False
            if isinstance(data, list):
                for entry in data:
                    item_name = entry.get('Leve Item', '').strip()
                    if not item_name:
                        continue
                    # Skip if ID already present
                    if entry.get('Leve Item ID') is not None:
                        continue

                    market_id = get_market_id(driver, item_name)
                    entry['Leve Item ID'] = market_id
                    updated = True
                    print(f"{fname}: '{item_name}' -> ID {market_id}")
            else:
                print(f"Skipping {file_path}: JSON root is not a list")
                continue

            if updated:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"Updated IDs in {file_path}\n")
                except Exception as e:
                    print(f"Failed to write {file_path}: {e}")
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
