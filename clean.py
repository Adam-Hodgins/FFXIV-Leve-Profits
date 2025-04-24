import os
import json
import re


def extract_amount(leve_item: str) -> int:
    """
    Extracts the numeric quantity from a "Leve Item" string.
    E.g., "Table Salt x 6" -> 6, "Budding Maple Wand" -> 1
    """
    match = re.search(r'x\s*(\d+)\s*$', leve_item, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 1


def clean_item_name(leve_item: str) -> str:
    """
    Removes a trailing " x N" from the item name.
    E.g., "Table Salt x 6" -> "Table Salt"; "Budding Maple Wand" -> "Budding Maple Wand"
    """
    # Strip off any "x <number>" at the end
    cleaned = re.sub(r'x\s*\d+\s*$', '', leve_item, flags=re.IGNORECASE)
    return cleaned.strip()


def main():
    directory = 'Clean Leves'

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
            for entry in data:
                item_text = entry.get('Leve Item', '')
                amount = extract_amount(item_text)
                name_only = clean_item_name(item_text)

                if entry.get('Leve Amount') != amount:
                    entry['Leve Amount'] = amount
                    updated = True

                if entry.get('Leve Item') != name_only:
                    entry['Leve Item'] = name_only
                    updated = True
        else:
            print(f"Skipping {file_path}: JSON root is not a list")
            continue

        if updated:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Updated Leve Amounts and cleaned items in {file_path}")
            except Exception as e:
                print(f"Failed to write {file_path}: {e}")


if __name__ == '__main__':
    main()
