import csv 

new_csv_data = []
files= [    
        'EURUSD_Candlestick_1_M_BID_01.01.2025-06.05.2025.csv',
        'EURUSD_Candlestick_1_M_BID_05.05.2025-02.09.2025.csv',
        'EURUSD_Candlestick_1_M_BID_01.09.2025-02.12.2025.csv',
        'EURUSD_Candlestick_1_M_BID_01.12.2025-19.01.2026.csv',
        'EURUSD_Candlestick_1_M_BID_19.01.2026-30.01.2026.csv',
        'DAT_MT_EURUSD_M1_202602.csv']

for i in range(len(files)):
    with open(files[i]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[0] == 'Day' and row[1] == 'Hour':
                gmt_time = []
                gmt_time.append[row['Day'],row['Hour']] 
                new_csv_data.append([
                gmt_time, 
                row['Open'],
                row['High'],
                row['Low'],
                row['Close'],
                row['Volume']])
            else:
                new_csv_data.append([
                row['Gmt time'],
                row['Open'],
                row['High'],
                row['Low'],
                row['Close'],
                row['Volume']
            ])
with open('EURUSD_Candlesticks_1_M_BID_01.01.2025-30.01.2026.csv','w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        'Gmt time','Open','High',
        'Low','Close','Volume'
    ])
    writer.writerows(new_csv_data)
