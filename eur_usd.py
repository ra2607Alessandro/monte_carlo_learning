#calculate volatility
import pandas as pd
import numpy as np
df = pd.read_csv('EUR_USD.csv').set_index('Date')
df = df.sort_index() # from old to new 

price = df['Close'].astype(float)
log_ret = np.log(price/price.shift(1)).dropna()
df['log_ret'] = log_ret

TRADING_DAYS = 252
windows = [10, 20, 60]
 
for window in windows:

     col = f'vol_{window}d'
     df[col] = df['log_ret'].rolling(window).std() * np.sqrt(TRADING_DAYS)
     print(df[col])

      


def MA(period,price):
      return price.rolling(period).mean()
    
          
#calculate 50-day MA
print(MA(period=50,price=price))

#calculate 200-day MA
print(MA(period=200,price=price))