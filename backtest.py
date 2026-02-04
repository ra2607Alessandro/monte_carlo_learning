import pandas as pd
import datetime 

df = pd.read_csv('EURUSD_Candlesticks_1_M_BID_01.01.2025-30.01.2026.csv')
df['Gmt time'] = pd.to_datetime(df['Gmt time'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Gmt time']).sort_values('Gmt time').reset_index(drop=True)
df['date'] = df['Gmt time'].dt.date
df['hour'] = df['Gmt time'].dt.hour

def get_asian_date(day,month,year):
  date_real = f'{day}.{month}.{year}' 
  for i in range (1,8): 
   morning_asian_session = df[(df['Gmt time'] == f'{date_real} {datetime.time(hour=i,minute=0,second=0,microsecond=0)}') &
                    (df['Gmt time'] == f'{date_real} {datetime.time(hour=8,minute=0,second=0,microsecond=0)}')]
  
   afternoon_asian_session = df[(df['Gmt time'] == f'{date_real} {datetime.time(hour=8,minute=0,second=0,microsecond=0)}') &
                    (df['Gmt time'] == f'{date_real} {datetime.time(hour=14,minute=0,second=0,microsecond=0)}')]

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


get_asian_date(30,'01',2026)

def breakouts(range_high,range_low,session,date):
  if session.lower() == 'london':
    start_hour, end_hour = 8, 11
  if session.lower() == 'new york':
    start_hour,end_hour = 14, 18

  for i in range(start_hour,end_hour):
     session_data = df[(df['Gmt time'] == f'{date} {datetime.time(hour=i,minute=0,second=0,microsecond=0)}') &
                    (df['Gmt time'] == f'{date} {datetime.time(hour=end_hour,minute=0,second=0,microsecond=0)}')]
  
     if len(session_data) == 0:
      return None
  
     long_breakout = session_data[session_data['Close'] > range_high ]
     if len(long_breakout) > 0:
        
        first_break = long_breakout.iloc[0]
        # Check if price stayed above for 15 minutes (15 candles)
        break_hold = first_break['Gmt time']
        for i in range(15):
          
        
        # Check for breakout below range low
        # Confirmed breakout