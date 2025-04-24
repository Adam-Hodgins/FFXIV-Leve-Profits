import os
import glob
import json
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

def process_dataframe(records):
    df = pd.DataFrame(records)
    # Numeric conversions
    df['Leve Amount'] = pd.to_numeric(df.get('Leve Amount', 1), errors='coerce').fillna(1)
    df['Leve Gil'] = (
        df.get('Leve Gil', '')
        .astype(str)
        .str.replace(',', '', regex=False)
        .astype(float)
    )
    # Additional metrics
    df['LevePriceNQ'] = df['currentAveragePriceNQ'] * df['Leve Amount']
    df['LevePriceHQ'] = df['currentAveragePriceHQ'] * df['Leve Amount']
    df['LeveProfitNQ'] = df['Leve Gil'] - df['LevePriceNQ']
    df['LeveProfitHQ'] = - (df['Leve Gil'] * 2) - df['LevePriceHQ']
    return df

def main():
    directory = 'Prepped Leves'
    pattern = os.path.join(directory, '*.json')
    files = glob.glob(pattern)

    if not files:
        print(f'No JSON files found in {directory}')
        return

    output_file = 'Leve Profits.xlsx'

    # Write each DataFrame to its own sheet using openpyxl engine
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for file_path in sorted(files):
            fname = os.path.basename(file_path)
            sheet_name = os.path.splitext(fname)[0][:31]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                if not isinstance(records, list) or not records:
                    print(f"Skipping {fname}: no data to export")
                    continue
                df = process_dataframe(records)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Exported sheet '{sheet_name}' with {len(df)} records")
            except Exception as e:
                print(f"Error processing {fname}: {e}")

    # Re-open workbook and convert each sheet to an Excel Table
    wb = load_workbook(output_file)
    for ws in wb.worksheets:
        # Use sheet dimensions to define table ref
        ref = ws.dimensions
        tbl = Table(displayName=f"Table_{ws.title}", ref=ref)
        style = TableStyleInfo(
            name="TableStyleMedium9",
            showRowStripes=True,
            showColumnStripes=False
        )
        tbl.tableStyleInfo = style
        ws.add_table(tbl)
        print(f"Added table to sheet '{ws.title}'")

    wb.save(output_file)
    print(f"All sheets converted to tables in '{output_file}'")

if __name__ == '__main__':
    main()
