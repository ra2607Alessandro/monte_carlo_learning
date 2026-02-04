import pandas as pd
import datetime 

df = pd.read_csv('EURUSD_Candlesticks_1_M_BID_01.01.2025-30.01.2026.csv')

def get_asian_date(day,month,year)
  date_real = f'{day}.{month}.{year}' 
  morning_asian_session = df[(df['Gmt time'] == f'{date_real} {datetime.time(hour=0,minute=30,second=0,microsecond=0)}' &
                    df['Gmt time'] == f'{date_real} {datetime.time(hour=7,minute=30,second=0,microsecond=0)}')]

  range_high = morning_asian_session['High'].max()
  range_low = morning_asian_session['Low'].min()
  range_size = range_high - range_low
   
  print('Range High: ',range_high)
  print('Range Low: ',range_low)
  print('Range Size: ',range_size)


get_asian_date()