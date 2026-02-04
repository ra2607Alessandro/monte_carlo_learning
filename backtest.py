import pandas as pd
import datetime 

df = pd.read_csv('EURUSD_Candlesticks_1_M_BID_01.01.2025-30.01.2026.csv')

day = int(input('Day (i.e 23/1):'))
month = int(input('Month (i.e 7/1):'))
year = int(input('Year (i.e 2026/2000):'))
date = datetime.date(year=year,month=month,day=day)
date_real = f'{date.day}.{date.month}.{date.year}' 
asian_session = df[(df['Gmt time'] == f'{date_real} {datetime.time(hour=0,minute=30,second=0,microsecond=0)}' &
                    df['Gmt time'] == f'{date_real} {datetime.time(hour=7,minute=30,second=0,microsecond=0)}')]

range_high = asian_session['High'].max()
range_low = asian_session['Low'].min()
range_size = range_high - range_low
