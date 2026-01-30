import numpy as np
import pandas as pd
df = pd.read_csv("2EUR_USD.csv").set_index('Date')
df = df.sort_index()
# look at the 15 min chart when setting the ranges high and low
# London open 8.00 AM
# Wall Street open 15.30 PM

range_high = df['Range High'].astype(float)
range_low = df['Range Low'].astype(float)
m = 0.0015
print(f'Range High: {range_high.iloc[-1]:.5f}')
print(f'Range Low: {range_low.iloc[-1]:.5f}')
print(f'Stop Loss if High: {range_high.iloc[-1]-m :.5f}')
print(f'Stop Loss if Low: {range_low.iloc[-1]+ m :.5f}')
