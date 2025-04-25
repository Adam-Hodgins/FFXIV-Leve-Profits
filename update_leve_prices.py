import os
import json
import time
import requests

# === Configuration ===
WORLD = 'Famfrit'
API_URL = (
    'https://universalis.app/api/v2/{world}/{item_ids}'
    '?listings=0&entries=0'
    '&fields=items.currentAveragePrice%2Citems.currentAveragePriceNQ%2Citems.currentAveragePriceHQ'
)

BATCH_SIZE = 100      # up to 100 IDs per request
REQUEST_DELAY = 0.05  # seconds pause after each HTTP call

def fetch_prices_batch(item_ids, session):
    """
    Fetch prices for a list of item_ids and return a dict mapping each item_id to its price dict.
    """
    ids_csv = ','.join(str(i) for i in item_ids)
    url = API_URL.format(world=WORLD, item_ids=ids_csv)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('items', {})
    time.sleep(REQUEST_DELAY)
    return {int(k): v for k, v in data.items()}

def process_file(file_path, session):
    fname = os.path.basename(file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[{fname}] Failed to load: {e}")
        return

    if not isinstance(data, list):
        print(f"[{fname}] Skipping (root is not a list)")
        return

    # Clear old prices
    for entry in data:
        entry.pop('currentAveragePrice', None)
        entry.pop('currentAveragePriceNQ', None)
        entry.pop('currentAveragePriceHQ', None)

    # Map item IDs to their entries
    id_to_entries = {}
    for entry in data:
        iid = entry.get('Leve Item ID')
        if isinstance(iid, int):
            id_to_entries.setdefault(iid, []).append(entry)

    if not id_to_entries:
        print(f"[{fname}] No valid Leve Item IDs found")
        return

    all_ids = list(id_to_entries.keys())
    batches = [all_ids[i:i+BATCH_SIZE] for i in range(0, len(all_ids), BATCH_SIZE)]

    updated = False
    # Sequentially process each batch
    for batch in batches:
        try:
            prices_map = fetch_prices_batch(batch, session)
            for iid, price_info in prices_map.items():
                for entry in id_to_entries.get(iid, []):
                    entry['currentAveragePrice']   = price_info.get('currentAveragePrice')
                    entry['currentAveragePriceNQ'] = price_info.get('currentAveragePriceNQ')
                    entry['currentAveragePriceHQ'] = price_info.get('currentAveragePriceHQ')
            print(f"[{fname}] Updated batch IDs {batch}")
            updated = True
        except Exception as e:
            print(f"[{fname}] Error fetching batch {batch}: {e}")

    # Write back if updates occurred
    if updated:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[{fname}] File updated")
        except Exception as e:
            print(f"[{fname}] Failed to write: {e}")


def main():
    directory = 'Prepped Leves'
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return

    with requests.Session() as session:
        for fname in os.listdir(directory):
            if fname.lower().endswith('.json'):
                process_file(os.path.join(directory, fname), session)

if __name__ == '__main__':
    main()
