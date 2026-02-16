#calculate volatility
import pandas as pd
import numpy as np
df = pd.read_csv('EUR_USD.csv').set_index('Date')
df = df.sort_index() # from old to new 

def volatility():
  price = df['Close'].astype(float)
  log_ret = np.log(price/price.shift(1)).dropna()
  df['log_ret'] = log_ret

  TRADING_DAYS = 252
  windows = [10, 20, 60]

  for window in windows:
 
     col = f'vol_{window}d'
     df[col] = df['log_ret'].rolling(window).std() * np.sqrt(TRADING_DAYS)
     for w in windows:
        if w == 10:
          col = f'vol_{w}d'
          vol = df[col].iloc[-1]
          return vol/np.sqrt(TRADING_DAYS)
        else:
          vol = df[f'vol_{w}d'].iloc[-1]
     

vol =volatility()
print(vol)
      

def margin(daily_market_movements):
  return daily_market_movements * 0.25

m = margin(vol)



