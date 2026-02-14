import csv 

new_csv = []

with open('GBPUSD_M1.csv') as csvfile:
    # Skip header line
    next(csvfile)
    
    for line in csvfile:
        # Split by any whitespace
        values = line.strip().split()
        
        # Combine date and time if they're separate (e.g., "2025-11-04" and "14:01:00")
        if len(values) == 7:
            time_value = f"{values[0]} {values[1]}"
            data = [time_value, values[2], values[3], values[4], values[5], values[6]]
        else:
            data = values
        
        new_csv.append(data)

# Write as comma-separated
with open('GBPUSD_M1_formatted.csv', 'w', newline='') as newfile:
    writer = csv.writer(newfile)
    writer.writerow(['Gmt time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    writer.writerows(new_csv)

print(f"Done! Converted {len(new_csv)} rows")