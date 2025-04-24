import os
import json
import time
import requests

# === Configuration ===
# Change this to target a different server
WORLD = 'Famfrit'

API_URL = (
    'https://universalis.app/api/v2/{world}/{item_id}'
    '?listings=0&entries=0'
    '&fields=currentAveragePrice%2CcurrentAveragePriceNQ%2CcurrentAveragePriceHQ'
)


def fetch_prices(item_id: int) -> dict:
    """
    Fetches average price data for a given item ID from Universalis.
    Returns dict with keys 'currentAveragePrice', 'currentAveragePriceNQ', 'currentAveragePriceHQ'.
    Refer to https://docs.universalis.app/ if you want to change/update the fields returned
    """
    url = API_URL.format(world=WORLD, item_id=item_id)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main():
    directory = 'Prepped Leves'
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return

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
            # Clear existing price fields
            for entry in data:
                entry.pop('currentAveragePrice', None)
                entry.pop('currentAveragePriceNQ', None)
                entry.pop('currentAveragePriceHQ', None)

            # Fetch fresh prices
            for entry in data:
                item_id = entry.get('Leve Item ID')
                if not isinstance(item_id, int):
                    continue

                try:
                    prices = fetch_prices(item_id)
                    entry['currentAveragePrice'] = prices.get('currentAveragePrice')
                    entry['currentAveragePriceNQ'] = prices.get('currentAveragePriceNQ')
                    entry['currentAveragePriceHQ'] = prices.get('currentAveragePriceHQ')
                    updated = True
                    print(f"{fname}: Refreshed prices for ID {item_id}")
                except Exception as e:
                    print(f"Error fetching prices for ID {item_id}: {e}")

                # Pause to avoid rate limiting
                time.sleep(0.2)
        else:
            print(f"Skipping {file_path}: root JSON is not a list")
            continue

        if updated:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Updated prices in {file_path}\n")
            except Exception as e:
                print(f"Failed to write {file_path}: {e}")

if __name__ == '__main__':
    main()
