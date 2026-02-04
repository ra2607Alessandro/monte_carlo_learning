import pandas as pd
import datetime 

df = pd.read_csv('EURUSD_Candlesticks_1_M_BID_01.01.2025-30.01.2026.csv')

def get_asian_date(day,month,year):
  date_real = f'{day}.{month}.{year}' 
  morning_asian_session = df[(df['Gmt time'] == f'{date_real} {datetime.time(hour=0,minute=30,second=0,microsecond=0)}' &
                    df['Gmt time'] == f'{date_real} {datetime.time(hour=7,minute=30,second=0,microsecond=0)}')]
  
  afternoon_asian_session = df[(df['Gmt time'] == f'{date_real} {datetime.time(hour=9,minute=0,second=0,microsecond=0)}' &
                    df['Gmt time'] == f'{date_real} {datetime.time(hour=15,minute=0,second=0,microsecond=0)}')]

  range_high_mornig = morning_asian_session['High'].max()
  range_low_morning = morning_asian_session['Low'].min()
  range_size_morning = range_high_mornig - range_low_morning
   
  range_high_afternoon = afternoon_asian_session["High"].max()
  range_low_afternoon = afternoon_asian_session["Low"].min()
  range_size_afternoon = range_high_afternoon - range_low_afternoon

  print('Range High (Morning) : ',range_high_mornig)
  print('Range Low (Morning) : ',range_low_morning)
  print('Range Size (Morning) : ',range_size_morning)
  print('Range High (Afternoon) : ',range_high_afternoon)
  print('Range Low (Afternoon) : ',range_low_afternoon)
  print('Range Size (Afternoon) : ',range_size_afternoon)


get_asian_date()

def breakouts():