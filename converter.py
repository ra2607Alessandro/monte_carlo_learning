import csv 

new_csv_data = []
files= ['EURUSD_1_M_BID_19.01.2026-30.01.2026.csv','EURUSD_1_M_BID_01.12.2025-19.01.2026.csv','EURUSD_1_M_BID_19.01.2026-30.01.2026.csv',
        'EURUSD_1_M_BID_01.09.2025-02.12.2025.csv','EURUSD_1_M_BID_05.05.2025-02.09.2025.csv','EURUSD_1_M_BID_01.01.2025-06.05.2025.csv']

for file in files:
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            new_csv_data.append([
                row['Gmt time'],
                row['Open'],
                row['High'],
                row['Low'],
                row['Close'],
                row['Volume']
            ])
