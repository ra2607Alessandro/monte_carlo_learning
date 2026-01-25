#calculate volatility
import pandas as pd
import numpy as np
df = pd.read_csv('EUR_USD.csv').set_index('Date')
df = df.sort_index() # from old to new 

price = float(df['Close'])
log_ret = np.log(price/price.shift(1)).dropna()
df['log_ret'] = log_ret

window = [10, 20, 60]
 
for i in range(len(window)):

    standard_deviation = df['log_ret'].rolling(i).std()
    print(f'Standard deviation in {i}-days:{standard_deviation}') 

   
    

#calculate 50-day MA
#calculate 200-day MA