import pandas as pd
import datetime 

df = pd.read_csv('EURUSD_Candlesticks_1_M_BID_01.01.2025-30.01.2026.csv')
df['Gmt time'] = pd.to_datetime(df['Gmt time'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Gmt time']).sort_values('Gmt time').reset_index(drop=True)
df['date'] = df['Gmt time'].dt.date
df['hour'] = df['Gmt time'].dt.hour

def get_asian_date(date):
   
  morning_asian_session = df[(df['date'] == date) & (df['hour'].between(1,7))]
  
  
  afternoon_asian_session = df[(df['date'] == date) & (df['hour'].between(8,13))]

  range_high_morning = morning_asian_session['High'].max()
  range_low_morning = morning_asian_session['Low'].min()
  range_size_morning = range_high_morning - range_low_morning
   
  range_high_afternoon = afternoon_asian_session["High"].max()
  range_low_afternoon = afternoon_asian_session["Low"].min()
  range_size_afternoon = range_high_afternoon - range_low_afternoon

  print('Range High (Morning) : ',range_high_morning)
  print('Range Low (Morning) : ',range_low_morning)
  print('Range Size (Morning) : ',range_size_morning)
  print('Range High (Afternoon) : ',range_high_afternoon)
  print('Range Low (Afternoon) : ',range_low_afternoon)
  print('Range Size (Afternoon) : ',range_size_afternoon)



def breakouts(range_high,range_low,session,date):
  if session.lower() == 'london':
    start_hour, end_hour = 8, 11
  elif session.lower() == 'new york':
    start_hour,end_hour = 14, 18
  else:
    return None


  session_data = df[(df['date'] == date) & (df['hour'].between(start_hour,end_hour))] 
  session_df = session_data.copy()

  if len(session_df) == 0:
      return None
  
  long_breakout = session_df[session_df['Close'] > range_high ].index
  if len(long_breakout) > 0:
        
        first_break = long_breakout[0]
        # Check if price stayed above for 15 minutes (15 candles)
        idx = first_break.name
        
        closes = df.loc[idx+1:idx+15,'Close']

        if len(closes) == 15:
           counter = int((closes > range_high).sum()) 
           entry_idx = first_break + len(closes) + 1
        else:
           return None
          
        return {
            ' Breakout above range high after first': counter,
            ' Rate of Confidence in breakout': (counter/15) * 100,
            ' Entry':entry_idx
          }
    
    # Check for breakout below range low
  short_breakout = session_df[session_df['Close'] < range_low].index
  if len(short_breakout) > 0:
        
        first_break = short_breakout[0]
        # Check if price stayed below for 15 minutes (15 candles)
        idx = first_break.name
        
       
        closes = df.loc[idx:idx+14,'Close']

        if len(closes) == 15:
          counter = int((closes < range_low).sum())
          entry_idx = first_break + len(closes) + 1
        else:
           return None
          
        return {
            ' Breakout below range low after first' : counter,
            ' Rate of Confidence in breakout': (counter/15) * 100,
            ' Entry': entry_idx
          }
        
        # Confirmed breakout
  
def trades(entry_idx, direction, entry_price, tp, end_dat,range_size):
   
   stop_loss = entry_price - 0.0015

   if direction.lower == 'long':
    take_profit = entry_price + (tp *range_size)
   elif direction.lower == 'short':
    take_profit = entry_price - (tp *range_size)
   else:
      raise ValueError('Direction is either "long" or "short"')
   
   
   