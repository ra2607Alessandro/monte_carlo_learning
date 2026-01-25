#calculate volatility
import pandas as pd
import numpy as np
df = pd.read_csv('EUR_USD.csv').set_index('Date')
df = df.sort_index() # from old to new 

price = df['Close'].astype(float)
log_ret = np.log(price/price.shift(1)).dropna()
df['log_ret'] = log_ret

window = [10, 20, 60]
 
for i in range(len(window)):

      standard_deviation = log_ret.rolling(i).std()
      print(f'Standard deviation in {i}-days:{standard_deviation}') 


def MA(period,price):
      return price.rolling(period).mean()
    
          
#calculate 50-day MA
print(MA(period=50,price=price))

#calculate 200-day MA
print(MA(period=200,price=price))