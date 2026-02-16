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
     

      


def MA(period,price):
      return price.rolling(period).mean()
    
          
#calculate 50-day MA
df['sma_50'] = MA(period=50,price=price)

#calculate 200-day MA
df['sma_200'] = MA(period=200,price=price)

print("Latest price:", price.iloc[-1])
for w in windows:
    if w == 10:
       col = f'vol_{w}d'
       print(f"{w}-day annualized vol (latest): {df[col].iloc[-1]:.4%}")  
       print(f'Daily Market Movemets: {df[col].iloc[-1]/np.sqrt(TRADING_DAYS):.4%}')
    else: 
      print(f"{w}-day annualized vol (latest): {df[f'vol_{w}d'].iloc[-1]:.4%}")
print("SMA50 (latest):", df['sma_50'].iloc[-1])
print("SMA200 (latest):", df['sma_200'].iloc[-1])



def margin(x):
  return x*0.25


