import pandas as pd

# Load the data
df = pd.read_csv('EUR_USD.csv')

# Ensure sorted oldest to newest
df = df.sort_values('Date').reset_index(drop=True)

# Calculate True Range
df['H-L']  = df['High'] - df['Low']
df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
df['L-PC'] = abs(df['Low']  - df['Close'].shift(1))

df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)

# Calculate ATR(14) using Wilder's smoothing (RMA)
period = 14
df['ATR_14'] = df['TR'].ewm(alpha=1/period, min_periods=period, adjust=False).mean()

atr = df['ATR_14'].iloc[-1]
# Show the last 14 rows
print(df[['Date', 'High', 'Low', 'Close', 'TR', 'ATR_14']].tail(14).to_string(index=False))
print(f"\nLatest ATR(14): {atr:.5f}")

def accept(range_high, range_low):
    range_size = abs(range_high - range_low)
    if range_size < 0.3*atr or range_size > 2.0*atr:
        print('Not tradeable')
    else:
        print('tradeable')

today = accept(range_high=1.18195,range_low=1.17885)
print(today)