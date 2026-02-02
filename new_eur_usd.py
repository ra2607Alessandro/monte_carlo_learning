import pandas as pd

# Read dates correctly (day-first format in the CSV) and sort by Date and Hour Range
df = pd.read_csv("2EUR_USD.csv", dayfirst=True, parse_dates=['Date'])
df = df.sort_values(['Date', 'Hour Range'])

# Take the last row (chronologically latest)
last = df.iloc[-1]
range_high = float(last['Range High'])
range_low = float(last['Range Low'])
m = 0.0015
print(f"Range High: {range_high:.5f}")
print(f"Range Low: {range_low:.5f}")
print(f"Stop Loss if High: {range_high - m:.5f}")
print(f"Stop Loss if Low: {range_low + m:.5f}")
