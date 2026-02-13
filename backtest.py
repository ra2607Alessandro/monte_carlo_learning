import pandas as pd
import datetime
import numpy as np

# Load and preprocess data
# parse datetimes (dayfirst True) and drop rows where parsing failed
df = pd.read_csv('GBPUSD_M1.csv')
if 'Time' not in df.columns:
   time_col = df.columns[0]
   df.rename(columns={time_col:'Time'},inplace=True)
df['Time'] = pd.to_datetime(df['Time'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Time']).sort_values('Time').reset_index(drop=True)
# convenience columns
df['date'] = df['Time'].dt.date
df['hour'] = df['Time'].dt.hour

# Constants (tweakable)
CONFIRM_MINUTES = 15

def _range_from_mask(mask):
      part = df[mask]
      if part.empty:
         return None
      highest_open = part['High'].max()
      lowest_close = part['Low'].min()
      size = highest_open - lowest_close
 
      return {'high': float(highest_open), 'low': float(lowest_close), 'size': float(size)}

def get_asian_date(date):
   """
   Compute Asian session ranges for a given `date`.

   Returns a dict with keys 'morning' and 'afternoon'. Each value is either
   None (if session has no candles) or a dict with 'high', 'low', 'size'.

   Uses hours:
     - morning: hours 1..7 inclusive
     - afternoon: hours 8..13 inclusive

   Note: `df['hour']` contains integer hour values (0-23). We use
   boolean masking via `df[mask]` to select rows for the session.
   """
   morning_mask = (df['date'] == date) & (df['hour'].between(1, 7))
   afternoon_mask = (df['date'] == date) & (df['hour'].between(8, 13))

   
   return {'morning': _range_from_mask(morning_mask), 'afternoon': _range_from_mask(afternoon_mask)}


def breakouts(range_high, range_low, session, date, confirm_minutes=CONFIRM_MINUTES):
   """
   Detect and (attempt to) confirm a breakout within a session on `date`.

   Parameters
   - range_high, range_low: numeric Asian session boundaries
   - session: 'london' or 'new york'
   - date: date object to search
   - confirm_minutes: number of subsequent candles to use for confirmation

   Returns a dict with:
     - 'direction': 'long' or 'short'
     - 'first_break_idx': integer index of first breakout candle in `df`
     - 'entry_idx': integer index to enter (first candle after confirmation)
     - 'counter': number of confirming candles (0..confirm_minutes)
     - 'precision': counter/confirm_minutes
     - 'confirmed': boolean (True if precision == 1.0)
   Or returns None if no breakout or not enough data to confirm.

   Implementation notes:
   - select the whole session with a boolean mask (no per-hour loop)
   - use `.index` to get dataframe integer indices (not `.name` on Series)
   - slice next `confirm_minutes` candles with `df.loc[start:end, 'Close']` and
     count confirms using vectorized comparison, e.g. `(closes > range_high).sum()`
   """
   s = session.lower()
   if s == 'london':
      start_hour, end_hour = 8, 10
   elif s == 'new york':
      start_hour, end_hour = 14, 19
   else:
      return None

   # select session rows; inclusive between start_hour..end_hour
   mask = (df['date'] == date) & (df['hour'].between(start_hour, end_hour))
   session_df = df[mask]
   if session_df.empty:
      return None

   # find first long and short breakout indices (if any)
   long_idxs = session_df[session_df['Close'] > range_high].index
   short_idxs = session_df[session_df['Close'] < range_low].index

   def _confirm(first_idx, direction):
      # confirm uses next `confirm_minutes` candles strictly after first_idx
      start = int(first_idx) + 1
      end = start + int(confirm_minutes)
      if end > len(df):
         return None
      closes = df.loc[start:end - 1, 'Close']
      if len(closes) < confirm_minutes:
         return None
      if direction == 'long':
         counter = int((closes > range_high).sum())
      else:
         counter = int((closes < range_low).sum())
      precision = counter / float(confirm_minutes)
      entry_idx = end if end < len(df) else None
      return {
         'direction': direction,
         'first_break_idx': int(first_idx),
         'entry_idx': int(entry_idx) if entry_idx is not None else None,
         'counter': counter,
         'precision': precision,
      }

   if len(long_idxs):
      res = _confirm(long_idxs[0], 'long')
      if res:
         return res
   if len(short_idxs):
      res = _confirm(short_idxs[0], 'short')
      if res:
         return res
   return None


def trades(entry_idx, direction, tp_multiplier, range_size, max_hold_minutes=240):
   """
   Simulate a simple trade starting at `entry_idx`.

   - `entry_idx` must be an integer index into `df`.
   - `direction` is 'long' or 'short'.
   - `tp_multiplier` multiplies the Asian range size to set take-profit.
   - stop-loss is set to the opposite Asian boundary by the caller; here we
     approximate a simple fixed stop of 0.0015 if not provided.

   Returns a dict with entry/exit indices, prices, pnl (price units), duration and exit_reason.
   """
   if entry_idx is None or entry_idx >= len(df):
      return None

   entry_idx = int(entry_idx)
   entry_price = float(df.at[entry_idx, 'Open'])
   # default stop loss (caller should override if needed)
   default_sl_dist = 1.0
   if direction == 'long':
      tp = entry_price + tp_multiplier * range_size
      sl = entry_price - (range_size * default_sl_dist)
   elif direction == 'short':
      tp = entry_price - tp_multiplier * range_size
      sl = entry_price + (range_size * default_sl_dist)
   else:
      raise ValueError(f'direction is either "long" or "short" not {direction}')

   i = entry_idx
   minutes = 0
   exit_reason = 'timeout'
   exit_price = df.at[entry_idx, 'Close']

   # iterate candle by candle until TP/SL or timeout
   while i < len(df) and minutes < max_hold_minutes:
      o = float(df.at[i, 'Open'])
      h = float(df.at[i, 'High'])
      l = float(df.at[i, 'Low'])
      c = float(df.at[i, 'Close'])

      if direction == 'long':
         hit_tp = h >= tp
         hit_sl = l <= sl
         if hit_tp and not hit_sl:
            exit_price = tp
            exit_reason = 'tp'
            break
         if hit_sl and not hit_tp:
            exit_price = sl
            exit_reason = 'sl'
            break
         if hit_tp and hit_sl:
            # approximate which was hit first by distance from open
            exit_price = tp if abs(o - tp) < abs(o - sl) else sl
            exit_reason = 'tp' if exit_price == tp else 'sl'
            break
      elif direction == 'short':  # short
         hit_tp = l <= tp
         hit_sl = h >= sl
         if hit_tp and not hit_sl:
            exit_price = tp
            exit_reason = 'tp'
            break
         if hit_sl and not hit_tp:
            exit_price = sl
            exit_reason = 'sl'
            break
         if hit_tp and hit_sl:
            exit_price = tp if abs(o - tp) < abs(o - sl) else sl
            exit_reason = 'tp' if exit_price == tp else 'sl'
            break
      else:
         raise ValueError(f'direction is either "long" or "short" not {direction}')

      minutes += 1
      i += 1

   # if loop ends without break, exit at last available close in that period
   if exit_reason == 'timeout':
      # ensure we use a valid index
      last_idx = min(i - 1, len(df) - 1)
      exit_price = float(df.at[last_idx, 'Close'])

   pnl = (exit_price - entry_price) if direction == 'long' else (entry_price - exit_price)
   duration = minutes
   return {
      'entry_idx': entry_idx,
      'entry_time': df.at[entry_idx, 'Time'],
      'entry_price': entry_price,
      'exit_price': exit_price,
      'exit_time': df.at[min(i, len(df) - 1), 'Time'],
      'direction': direction,
      'pnl': pnl,
      'duration_mins': duration,
      'exit_reason': exit_reason,
   }


def backtest(tp_multiplier=2.0, min_confidence=1.0):
      """
      Run the backtest over all dates in `df`.

      - `tp_multiplier`: multiple of Asian range used for take-profit
      - `min_confidence`: required precision (counter/confirm_minutes) to accept a breakout

      Returns a pandas DataFrame of trades.
      """
      trades_list = []
      for date in sorted(df['date'].unique()):
         asian = get_asian_date(date)
         # prefer morning range if available, else afternoon
         rng = asian.get('morning') or asian.get('afternoon')
         if not rng or rng['size'] == 0:
            continue
         if rng['size'] < 0.0015 or rng['size'] > 0.0050:
            continue
         #'london',
         for session in ('new york',):
            br = breakouts(rng['high'], rng['low'], session, date)
            if not br:
               continue
            if br.get('precision', 0.0) < float(min_confidence):
               continue
            entry_idx = br.get('entry_idx')
            if entry_idx is None:
               continue
            trade = trades(entry_idx, br['direction'], tp_multiplier, rng['size'])
            if trade:
               trade.update({'date': date, 'session': session, 'range_size': rng['size'], 'first_break_idx': br['first_break_idx'], 'precision': br['precision']})
               trades_list.append(trade)

      if not trades_list:
         return pd.DataFrame()
      else: 
         return pd.DataFrame(trades_list)



def sharpe_ratio(entry_price,pnl):
   Return = pnl/entry_price
   mean_return = np.mean(Return)
   sigma = np.std(Return)
   sr = mean_return/sigma
   return sr


results = backtest()
if results.empty:
   print("No trades")
else:
   total_pnl = results['pnl'].sum()
   wins = results[results['pnl'] > 0]
   winrate = (len(wins)/len(results))*100
   Sharpe_ratio = sharpe_ratio(entry_price=results[['entry_price']].values,pnl=results['pnl'].values)
   print(f'Trades: {len(results)}, Wins: {len(wins)}, Winrate: {winrate:.3f}')
   print(f'Total P&L: {total_pnl:.5f}')   
   print(f'Sharpe Ratio: {Sharpe_ratio:.5f}')

#add the sharpe ratio