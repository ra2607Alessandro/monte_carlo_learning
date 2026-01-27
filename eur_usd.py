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

Latest_price_23 = 1.1743
Latest_10d_annualized_vol_23 =  0.0064923
Latest_20d_annualized_vol_23 = 0.0049665
Latest_60d_annualized_vol_23 = 0.0043330
SMA50_23 = 1.1664539999999999
SMA200_23 = 1.1592449999999999

Latest_price_26 = 1.1869
Latest_10d_annualized_vol_26= 0.0078071
Daily_Market_Movemets_26= 0.0004918
Latest_20d_annualized_vol_26 = 0.0062816
Latest_60d_annualized_vol_26 = 0.0047283
SMA50_26 = 1.167008
SMA200_26 = 1.1595095

Latest_price_27 = 1.1876
Latest_10d_annualized_vol_27= 0.0077837
Daily_Market_Movemets_27 = 0.0004903
Latest_20d_annualized_vol_27 = 0.0062608
Latest_60d_annualized_vol_27 = 0.0046854
SMA50_27 = 1.167496
SMA200_27 = 1.159801

def margin():
    margin = Daily_Market_Movemets_27*0.25
    print(f'Margin: {margin:.4%} ')

margin()
