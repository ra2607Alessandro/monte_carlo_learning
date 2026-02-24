import csv
from datetime import datetime

new_csv_data = {}  # <-- dict instead of list, keyed by timestamp

files = [
    'EURUSD_Candlestick_1_M_BID_01.01.2025-06.05.2025.csv',
    'EURUSD_Candlestick_1_M_BID_05.05.2025-02.09.2025.csv',
    'EURUSD_Candlestick_1_M_BID_01.09.2025-02.12.2025.csv',
    'EURUSD_Candlestick_1_M_BID_01.12.2025-19.01.2026.csv',
    'EURUSD_Candlestick_1_M_BID_19.01.2026-30.01.2026.csv',
    'DAT_MT_EURUSD_M1_202602.csv',
    'EURUSD_M1.csv'
]

for i in range(len(files)):
    with open(files[i]) as csvfile:
        reader = csv.DictReader(csvfile)
        fieldname = reader.fieldnames
        print(files[i],fieldname)

        if 'Day' in fieldname and 'Hour' in fieldname:
            for row in reader:
                dt = datetime.strptime(f'{row["Day"]} {row["Hour"]}', '%Y.%m.%d %H:%M')
                gmt_time = dt.strftime('%d.%m.%Y %H:%M:%S.000')
                new_csv_data[gmt_time] = [row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]

        if 'Time' in fieldname or 'Time\tOpen\tHigh\tLow\tClose\tVolume' in fieldname:
            with open(files[i]) as file:
                read = csv.DictReader(file,delimiter='\t')
                for row in read:
                   dt = datetime.strptime(row['Time'], '%Y-%m-%d %H:%M:%S')
                   gmt_time = dt.strftime('%d.%m.%Y %H:%M:%S.000')
                   new_csv_data[gmt_time] = [row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]

        if 'Gmt time' in fieldname:
            for row in reader:
                gmt_time = row['Gmt time']
                new_csv_data[gmt_time] = [row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]

# Sort by timestamp before writing
sorted_data = sorted(new_csv_data.items(), key=lambda x: datetime.strptime(x[0], '%d.%m.%Y %H:%M:%S.000'))



with open('EURUSD_Candlesticks_1_M_BID_01.01.2025-20.02.2026.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Gmt time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    print(max(new_csv_data.keys()))
    for gmt_time, values in sorted_data:
        writer.writerow([gmt_time] + values)