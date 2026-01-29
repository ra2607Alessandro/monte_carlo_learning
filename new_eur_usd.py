import numpy as np
import pandas as pd
df = pd.read_csv("2EUR_USD.csv").set_index('Date')
df = df.sort_index()
# look at the 15 min chart when setting the ranges high and low
# London open 9.00 AM
# Wall Street open 15.30 PM

range_high = df['Range High']
range_low = df['Range Low']
print(f'Range High: {range_high.iloc[-1]}')
print(f'Range Low: {range_low.iloc[-1]}')