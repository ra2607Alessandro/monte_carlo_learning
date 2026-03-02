
import csv
from datetime import datetime

new_csv_data = {}  # keyed by timestamp to avoid duplicates

files = [
    'EURUSD_Candlestick_1_M_BID_01.01.2015-01.01.2016.csv',
    'EURUSD_Candlestick_1_M_BID_01.01.2016-01.01.2017.csv',
    'EURUSD_Candlestick_1_M_BID_01.01.2017-01.01.2018.csv',
    'EURUSD_Candlestick_1_M_BID_01.01.2018-01.01.2019.csv',
    'EURUSD_Candlestick_1_M_BID_01.01.2019-01.01.2020.csv',
    'EURUSD_Candlestick_1_M_BID_01.01.2020-01.01.2021.csv',
    'DAT_MT_EURUSD_M1_2021.csv',
    'DAT_MT_EURUSD_M1_2022.csv',
    'DAT_MT_EURUSD_M1_2023.csv',
    'DAT_MT_EURUSD_M1_2024.csv',
    'EURUSD_Candlesticks_1_M_BID_01.01.2025-13.02.2026.csv',
    'EURUSD_M1 (1).csv'
]

def detect_delimiter(filepath):
    """Detect whether file uses tab or comma as delimiter."""
    with open(filepath) as f:
        first_line = f.readline()
    return '\t' if '\t' in first_line else ','

def normalize_gmt(ts):
    """Parse a Gmt time string in any known variant, return a datetime object."""
    for fmt in ('%d.%m.%Y %H:%M:%S.000', '%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M'):
        try:
            return datetime.strptime(ts.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized timestamp format: '{ts}'")

for filepath in files:
    delimiter = detect_delimiter(filepath)
    print(f"Processing: {filepath} | delimiter: {'TAB' if delimiter == chr(9) else 'COMMA'}")

    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        fieldnames = reader.fieldnames
        print(f"  Fields: {fieldnames}")

        # --- Format 1: Day + Hour columns (e.g. Dukascopy style) ---
        if fieldnames and 'Day' in fieldnames and 'Hour' in fieldnames:
            for row in reader:
                try:
                    dt = datetime.strptime(f'{row["Day"]} {row["Hour"]}', '%Y.%m.%d %H:%M')
                    gmt_time = dt.strftime('%d.%m.%Y %H:%M:%S.000')
                    new_csv_data[gmt_time] = [row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]
                except (ValueError, KeyError) as e:
                    print(f"  Skipping row (Day/Hour format error): {e}")

        # --- Format 2: Tab-separated with 'Time' column (image 1 format) ---
        #     Input:  2025-11-20 14:34:00  (YYYY-MM-DD HH:MM:SS)
        #     Output: 20.11.2025 14:34:00.000 (DD.MM.YYYY HH:MM:SS.000)
        elif fieldnames and 'Time' in fieldnames:
            for row in reader:
                try:
                    dt = datetime.strptime(row['Time'].strip(), '%Y-%m-%d %H:%M:%S')
                    gmt_time = dt.strftime('%d.%m.%Y %H:%M:%S.000')
                    new_csv_data[gmt_time] = [
                        row['Open'].strip(),
                        row['High'].strip(),
                        row['Low'].strip(),
                        row['Close'].strip(),
                        row['Volume'].strip()
                    ]
                except (ValueError, KeyError) as e:
                    print(f"  Skipping row (Time format error): {e}")

        # --- Format 3: Gmt time column (Forex standard export) ---
        elif fieldnames and 'Gmt time' in fieldnames:
            for row in reader:
                try:
                    # Normalize: some files have 'DD.MM.YYYY HH:MM' (no seconds)
                    dt = normalize_gmt(row['Gmt time'])
                    gmt_time = dt.strftime('%d.%m.%Y %H:%M:%S.000')
                    new_csv_data[gmt_time] = [row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]
                except (ValueError, KeyError) as e:
                    print(f"  Skipping row (Gmt time error): {e}")

        else:
            print(f"  WARNING: Unrecognized format for {filepath}, skipping.")

# Sort all entries chronologically
sorted_data = sorted(
    new_csv_data.items(),
    key=lambda x: datetime.strptime(x[0], '%d.%m.%Y %H:%M:%S.000')
)

output_file = 'EURUSD_Candlesticks_1_M_BID_2015-01_03_2026.csv'
# Output format: DD.MM.YYYY HH:MM:SS.000,Open,High,Low,Close,Volume,
# No header row, comma-separated, trailing comma at end of each line
with open(output_file, 'w', newline='') as f:
    for gmt_time, (open_, high, low, close, volume) in sorted_data:
        f.write(f'{gmt_time},{open_},{high},{low},{close},{volume},\n')

print(f"\nDone! {len(sorted_data)} rows written to {output_file}")
if sorted_data:
    print(f"Date range: {sorted_data[0][0]} -> {sorted_data[-1][0]}")