import pandas as pd
import datetime
import numpy as np

# Load and preprocess data
# parse datetimes (dayfirst True) and drop rows where parsing failed
df = pd.read_csv('GBPUSD_M1.csv')
if 'Time' not in df.columns:
   time_col = df.columns[0]
   df.rename(columns={time_col:'Time'},inplace=True)
df['Time'] = pd.to_datetime(df['Time'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Time']).sort_values('Time').reset_index(drop=True)
# convenience columns
df['date'] = df['Time'].dt.date
df['hour'] = df['Time'].dt.hour
