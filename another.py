import pandas as pd
import datetime
import numpy as np

# Load and preprocess data
# parse datetimes (dayfirst True) and drop rows where parsing failed
df = pd.read_csv('GBPUSD_M1.csv', sep='\s+')
if 'Time' not in df.columns:
   time_col = df.columns[0]
   df.rename(columns={time_col:'Time'},inplace=True)
print(f'how many rows: {len(df)}')
print(f'Colums: {df.columns.to_list()}')
print(f'First Timestamps: {df['Time'].head()}')