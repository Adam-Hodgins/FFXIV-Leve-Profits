"""
Only need to use as a sanity check for new xpacs / leve updates
Checks the Clean Leves for any missing IDs and prints a list of the items with missing IDs for manual fetching from Universalis
"""
import os
import json


def main():
    directory = 'Clean Leves'
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return

    any_missing = False
    for fname in sorted(os.listdir(directory)):
        if not fname.lower().endswith('.json'):
            continue

        file_path = os.path.join(directory, fname)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            continue

        missing = []
        if isinstance(data, list):
            for entry in data:
                item_name = entry.get('Leve Item', '<Unknown>')
                item_id = entry.get('Leve Item ID')
                if not isinstance(item_id, int):
                    missing.append(item_name)
        else:
            print(f"Skipping {fname}: JSON root is not a list")
            continue

        if missing:
            any_missing = True
            print(f"\nIn {fname}, missing Leve Item ID for:")
            for name in missing:
                print(f"  - {name}")

    if not any_missing:
        print("All entries have valid Leve Item ID fields.")

if __name__ == '__main__':
    main()
