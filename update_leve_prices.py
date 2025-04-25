import os
import json
import time
import requests
from itertools import islice

# === Configuration ===
WORLD = 'Famfrit'
# Directory containing the leve JSON files
DIRECTORY = 'Clean Leves'

# API URL template; {ids} will be replaced with comma-separated list
API_URL = (
    'https://universalis.app/api/v2/{world}/{ids}'
    '?listings=0&entries=0'
    '&fields=currentAveragePrice%2CcurrentAveragePriceNQ%2CcurrentAveragePriceHQ'
)


def chunked_iterable(iterable, size):
    """Yield successive chunks of given size from iterable."""
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


def fetch_prices_batch(item_ids):
    """
    Fetch price data for a batch of item IDs from Universalis.
    Returns a dict: { item_id (int): {price fields} }
    """
    id_list = ','.join(str(i) for i in item_ids)
    url = API_URL.format(world=WORLD, ids=id_list)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    # If multiple IDs, response is keyed by ID strings
    # Convert keys to int for easy lookup
    return {int(k): v for k, v in data.items()}


def main():
    if not os.path.isdir(DIRECTORY):
        print(f"Directory not found: {DIRECTORY}")
        return

    for fname in sorted(os.listdir(DIRECTORY)):
        if not fname.lower().endswith('.json'):
            continue
        file_path = os.path.join(DIRECTORY, fname)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        except Exception as e:
            print(f"Failed to load {fname}: {e}")
            continue

        if not isinstance(entries, list):
            print(f"Skipping {fname}: JSON root is not a list")
            continue

        # Clear existing price fields
        for entry in entries:
            entry.pop('currentAveragePrice', None)
            entry.pop('currentAveragePriceNQ', None)
            entry.pop('currentAveragePriceHQ', None)

        # Collect unique valid IDs
        ids = sorted({entry.get('Leve Item ID') for entry in entries if isinstance(entry.get('Leve Item ID'), int)})
        if not ids:
            print(f"No valid item IDs in {fname}, skipping.")
            continue

        updated = False
        # Fetch in batches
        for batch in chunked_iterable(ids, 100):
            try:
                price_map = fetch_prices_batch(batch)
                print(f"Fetched prices for IDs: {batch}")
            except Exception as e:
                print(f"Error fetching batch {batch}: {e}")
                continue

            # Apply prices to entries
            for entry in entries:
                item_id = entry.get('Leve Item ID')
                if item_id in price_map:
                    prices = price_map[item_id]
                    entry['currentAveragePrice'] = prices.get('currentAveragePrice')
                    entry['currentAveragePriceNQ'] = prices.get('currentAveragePriceNQ')
                    entry['currentAveragePriceHQ'] = prices.get('currentAveragePriceHQ')
                    updated = True

            # Pause to respect rate limits
            time.sleep(0.2)

        # Write updated file if any changes
        if updated:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(entries, f, ensure_ascii=False, indent=2)
                print(f"Updated prices in {fname}\n")
            except Exception as e:
                print(f"Failed to write {fname}: {e}")

if __name__ == '__main__':
    main()
