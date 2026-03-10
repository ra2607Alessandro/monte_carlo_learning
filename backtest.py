import pandas as pd
import datetime
import numpy as np

# Load and preprocess data
files = ['EURUSD_Candlesticks_1_M_BID_01.01.2015-20.02.2026.csv','GBPUSD_Candlesticks_1_M_BID_2022-2026.csv']
daily = pd.read_csv('EUR_USD.csv')
daily = daily.groupby('Date').agg(
   High = ('High','max'),
   Low = ('Low','min'),
   Close=('Close', 'last')
   ).reset_index()
daily['tr'] = daily['High'] - daily['Low']
daily['atr'] = daily['tr'].rolling(14).mean()
daily = daily.set_index('Date')
daily.index = pd.to_datetime(daily.index, format='mixed').date

df = pd.read_csv('EURUSD_Candlesticks_1_M_BID_2015-01_01_2021.csv')
df['Gmt time'] = pd.to_datetime(df['Gmt time'], errors='coerce')
df = df.dropna(subset=['Gmt time']).sort_values('Gmt time').reset_index(drop=True)
df['date'] = df['Gmt time'].dt.date
df['hour'] = df['Gmt time'].dt.hour

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

   Returns a dict with two independent ranges:
     - 'morning'  : hours 1..7  GMT → used for the London session
     - 'afternoon': hours 8..13 GMT → used for the New York session

   Each value is either None (no candles) or a dict with 'high', 'low', 'size'.
   Neither range is a fallback for the other — they serve different sessions.
   """
   morning_mask   = (df['date'] == date) & (df['hour'].between(1, 7))
   afternoon_mask = (df['date'] == date) & (df['hour'].between(8, 13))
   return {
      'morning':   _range_from_mask(morning_mask),
      'afternoon': _range_from_mask(afternoon_mask)
   }


def breakouts(range_high, range_low, session, date, confirm_minutes=CONFIRM_MINUTES):
   """
   Detect and confirm a breakout within a session on `date`.

   Parameters
   - range_high, range_low: boundaries of the Asian range relevant to this session
   - session: 'london' or 'new york'
   - date: date object to search
   - confirm_minutes: number of subsequent candles used for confirmation

   Returns a dict with direction, first_break_idx, entry_idx, counter, precision.
   Returns None if no breakout or not enough data to confirm.
   """
   s = session.lower()
   if s == 'london':
      start_hour, end_hour = 8, 10
   elif s == 'new york':
      start_hour, end_hour = 14, 17
   else:
      return None

   mask = (df['date'] == date) & (df['hour'].between(start_hour, end_hour))
   session_df = df[mask]
   if session_df.empty:
      return None

   long_idxs  = session_df[session_df['Close'] > range_high].index
   short_idxs = session_df[session_df['Close'] < range_low].index

   def _confirm(first_idx, direction):
      start = int(first_idx) + 1
      end   = start + int(confirm_minutes)
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
         'direction':      direction,
         'first_break_idx': int(first_idx),
         'entry_idx':      int(entry_idx) if entry_idx is not None else None,
         'counter':        counter,
         'precision':      precision,
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


def trades(entry_idx, direction, tp_multiplier, range_size, max_hold_hours=10):
   """
   Simulate a trade starting at `entry_idx`.

   Risk rules applied inside the candle loop:
     - Rule 1 (Peak Profit Lock): if unrealized PnL reaches 70% of TP distance
       and then retraces to ≤30%, close the trade and lock in the gain.
     - Rule 2 (Breakeven Stop): once price moves 0.5× range_size in our favor,
       ratchet the SL to entry price so we can never lose on this trade.

   Returns a dict with entry/exit prices, pnl, duration and exit_reason.
   """
   if entry_idx is None or entry_idx >= len(df):
      return None

   entry_idx   = int(entry_idx)
   entry_price = float(df.at[entry_idx, 'Open'])
   default_sl  = 0.8

   if direction == 'long':
      tp = entry_price + tp_multiplier * range_size
      sl = entry_price - (range_size * default_sl)
   elif direction == 'short':
      tp = entry_price - tp_multiplier * range_size
      sl = entry_price + (range_size * default_sl)
   else:
      raise ValueError(f'direction must be "long" or "short", got {direction}')

   i                = entry_idx
   minutes          = 0
   hours            = 0
   exit_reason      = 'timeout'
   exit_price       = df.at[entry_idx, 'Close']
   max_hold_minutes = max_hold_hours * 60

   # ── Rule 1: Peak Profit Lock ───────────────────────────────────────────────
   #peak_pnl    = 0.0
   #tp_distance = abs(tp - entry_price)
   # ──────────────────────────────────────────────────────────────────────────

   while i < len(df) and minutes < max_hold_minutes and hours < max_hold_hours:
      o = float(df.at[i, 'Open'])
      h = float(df.at[i, 'High'])
      l = float(df.at[i, 'Low'])
      c = float(df.at[i, 'Close'])

      # ── Rule 1: update peak unrealized PnL using candle High/Low ────────────
      #if direction == 'long':
       #  unrealized_peak = h - entry_price
      #else:
       #  unrealized_peak = entry_price - l
      #peak_pnl = max(peak_pnl, unrealized_peak)

      # If we've reached 70% of TP distance, don't let it fall below 30%
      #if peak_pnl >= 0.70 * tp_distance:
       #  current_unrealized = (c - entry_price) if direction == 'long' else (entry_price - c)
        # if current_unrealized <= 0.30 * tp_distance:
         #   exit_price  = c
          #  exit_reason = 'trail_lock'
           # break
      # ────────────────────────────────────────────────────────────────────────

      # ── Rule 2: Breakeven Stop ───────────────────────────────────────────────
      # if  direction == 'long' and l > entry_price:
       #  if (h - entry_price) >= (range_size * 0.5):
        #    sl = max(sl, entry_price)   # ratchet up to entry, never back down
      #elif direction == 'short' and h < entry_price:
       #  if (entry_price - l) >= (range_size * 0.5):
        #    sl = min(sl, entry_price)   # ratchet down to entry, never back up
      # ────────────────────────────────────────────────────────────────────────

      if direction == 'long':
         hit_tp = h >= tp
         hit_sl = l <= sl
         if hit_tp and not hit_sl:
            exit_price = tp;  exit_reason = 'tp'; break
         if hit_sl and not hit_tp:
            exit_price = sl;  exit_reason = 'sl'; break
         if hit_tp and hit_sl:
            exit_price  = tp if abs(o - tp) < abs(o - sl) else sl
            exit_reason = 'tp' if exit_price == tp else 'sl'
            break
      else:
         hit_tp = l <= tp
         hit_sl = h >= sl
         if hit_tp and not hit_sl:
            exit_price = tp;  exit_reason = 'tp'; break
         if hit_sl and not hit_tp:
            exit_price = sl;  exit_reason = 'sl'; break
         if hit_tp and hit_sl:
            exit_price  = tp if abs(o - tp) < abs(o - sl) else sl
            exit_reason = 'tp' if exit_price == tp else 'sl'
            break

      minutes += 1
      if minutes == 59:
         hours   += 1
         minutes  = 0
      i += 1

   if exit_reason == 'timeout':
      last_idx   = min(i - 1, len(df) - 1)
      exit_price = float(df.at[last_idx, 'Close'])

   pnl      = (exit_price - entry_price) if direction == 'long' else (entry_price - exit_price)
   duration = minutes
   return {
      'entry_idx':    entry_idx,
      'entry_time':   df.at[entry_idx, 'Gmt time'],
      'entry_price':  entry_price,
      'exit_price':   exit_price,
      'exit_time':    df.at[min(i, len(df) - 1), 'Gmt time'],
      'direction':    direction,
      'pnl':          pnl,
      'duration_mins': duration,
      'exit_reason':  exit_reason,
   }


def backtest(tp_multiplier=2.0, min_confidence=1.0):
   """
   Run the backtest over all dates in `df`.

   - Morning Asian range (01:00–07:00 GMT) is used exclusively for the London session.
   - Afternoon Asian range (08:00–13:00 GMT) is used exclusively for the New York session.
   - If the required range for a session is missing, that session is skipped.

   Returns a pandas DataFrame of trades.
   """
   trades_list       = []
   total_dates       = 0
   no_asian_range    = 0
   range_outside_atr = 0
   no_breakouts      = 0
   ema_killed        = 0
   trades_taken      = 0

   df['ema50'] = df['Close'].shift(1).ewm(span=50, adjust=False).mean()

   # Map each session to the Asian range it should use
   session_range_key = {
      'london':   'morning',    # 01:00–07:00 GMT range
      'new york': 'afternoon',  # 08:00–13:00 GMT range
   }

   for date in sorted(df['date'].unique()):
      past_daily = daily[daily.index < date]
      total_dates += 1

      if len(past_daily) < 14:
         continue
      recent_atr = past_daily['atr'].iloc[-1]
      if pd.isna(recent_atr):
         continue

      asian = get_asian_date(date)

      for session, range_key in session_range_key.items():
         # Each session uses its own dedicated Asian range
         rng = asian.get(range_key)

         if not rng or rng['size'] == 0:
            no_asian_range += 1
            continue

         # ATR band filter applied per-session range
         if rng['size'] < 0.3 * recent_atr or rng['size'] > 2.0 * recent_atr:
            range_outside_atr += 1
            continue

         br = breakouts(rng['high'], rng['low'], session, date)
         if not br:
            no_breakouts += 1
            continue

         entry_idx   = br.get('entry_idx')
         if entry_idx is None:
            continue
         entry_price = df.at[entry_idx, 'Open']

         # EMA filter
         if br['direction'] == 'long' and entry_price < df.at[entry_idx, 'ema50']:
            ema_killed += 1
            continue
         if br['direction'] == 'short' and entry_price > df.at[entry_idx, 'ema50']:
            ema_killed += 1
            continue

         if br.get('precision', 0.0) < float(min_confidence):
            continue

         trade = trades(entry_idx, br['direction'], tp_multiplier, rng['size'])
         if trade:
            trades_taken += 1
            trade.update({
               'date':            date,
               'session':         session,
               'range_key':       range_key,
               'range_size':      rng['size'],
               'first_break_idx': br['first_break_idx'],
               'precision':       br['precision'],
            })
            trades_list.append(trade)

   print(f"Total trading days:        {total_dates}")
   print(f"No asian range:            {no_asian_range}")
   print(f"Range outside ATR band:    {range_outside_atr}")
   print(f"No breakout found:         {no_breakouts}")
   print(f"EMA filter rejected:       {ema_killed}")
   print(f"Trades taken:              {trades_taken}")

   if not trades_list:
      return pd.DataFrame()
   return pd.DataFrame(trades_list)


def sharpe_ratio(pnl, entry_price, trades_per_year=None):
   """
   Chan-style annualised Sharpe Ratio.
   """
   returns     = pnl / entry_price.flatten()
   mean_return = np.mean(returns)
   sigma       = np.std(returns, ddof=1)

   if sigma == 0:
      return 0.0

   if trades_per_year is None:
      n_years       = (results['entry_time'].max() - results['entry_time'].min()).days / 365.25
      trades_per_year = len(returns) / n_years

   return (mean_return / sigma) * np.sqrt(trades_per_year)


results = backtest()
if results.empty:
   print("No trades")
else:
   exit_reasons = results.groupby('exit_reason')['pnl'].agg(['mean', 'count'])
   total_pnl    = results['pnl'].sum()
   wins         = results[results['pnl'] > 0]
   winrate      = (len(wins) / len(results)) * 100
   Sharpe_ratio = sharpe_ratio(
      entry_price=results[['entry_price']].values,
      pnl=results['pnl'].values
   )
   T_stat = Sharpe_ratio * np.sqrt(int(2026 - 2015))
   print(f'exit reasons:\n{exit_reasons}')
   print(f'Trades: {len(results)}, Wins: {len(wins)}, Winrate: {winrate:.3f}')
   print(f'Total P&L: {total_pnl:.5f}')
   print(f'Sharpe Ratio: {Sharpe_ratio:.5f}')
   print(f'T statistic: {T_stat:5f}')