
import csv

new_csv = []
with open('GBPUSD_M1.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        new_csv.append([
            row['Time'],
            row['Open'],
            row['High'],
            row['Low'],
            row['Close'],
            row['Volume']
        ])

with open('GBPUSD_M1_formatted.csv') as newfile:
    writer = csv.DictWriter(newfile)
    writer.writerow([
        'Time','Open','High',
        'Low','Close','Volume'
    ])
    writer.writerows(new_csv)



