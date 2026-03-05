from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import numpy as np
from datetime import datetime, time as dt_time
import time



class BreakoutBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextId = None

        # Strategy Parameters
        self.symbol          = "EUR"
        self.currency        = "USD"
        self.confirm_minutes = 15
        self.tp_multiplier   = 2.0
        self.sl_multiplier   = 0.8

        # Asian Range — morning (01:00–07:00 GMT) → London session
        #             — afternoon (08:00–13:00 GMT) → New York session
        self.asian_high_morning   = None
        self.asian_low_morning    = None
        self.asian_high_afternoon = None
        self.asian_low_afternoon  = None

        # ATR — rolling 14 daily true ranges (each bar = one full trading day)
        self.daily_tr_list = []
        self.daily_atr     = None

        # EMA-50 — pre-seeded from last 50 historical 1-minute bars (reqId 3)
        #           then updated exponentially on every live bar
        self.ema_50          = None
        self.ema_bar_count   = 0       # tracks how many bars seen; <50 = seeding phase
        self.ema_span        = 50
        self.ema_k           = 2 / (self.ema_span + 1)
        self.ema_seed_closes = []      # accumulates last 50 historical closes for seed

        # State Machine
        self.in_position         = False
        self.potential_direction = None
        self.confirm_closes      = []     # sequential closes after first break candle
        self.pending_entry       = False  # True = confirmed, enter on next bar open

    # ------------------------------------------------------------------ #
    #  CONNECTION                                                          #
    # ------------------------------------------------------------------ #
    def nextValidId(self, orderId):
        self.nextId = orderId

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson="", contract=None):
        if errorCode not in [2104, 2106, 2158]:
            print(f"Error {errorCode}: {errorString}")

    # ------------------------------------------------------------------ #
    #  1. DATA COLLECTION                                                  #
    # ------------------------------------------------------------------ #
    def historicalData(self, reqId, bar):
        # reqId 1 — daily bars → 14-period ATR
        #           each bar represents one full trading day (High - Low = daily TR)
        if reqId == 1:
            tr = bar.high - bar.low
            self.daily_tr_list.append(tr)
            if len(self.daily_tr_list) > 14:
                self.daily_tr_list.pop(0)

        # reqId 2 — 1-minute bars → split into morning / afternoon Asian ranges
        if reqId == 2:
            if isinstance(bar.date, (int, float)):
              bar_dt = datetime.fromtimestamp(bar.date, tz=timezone.utc)
            else:
              date_str = bar.date.strip().split(" ")[0] + " " + bar.date.strip().split(" ")[1]
              bar_dt = datetime.strptime(date_str, "%Y%m%d %H:%M:%S")

            
            h = bar_dt.hour

            # Morning range: 01:00–07:00 GMT → used for London session
            if 1 <= h <= 7:
                if self.asian_high_morning is None or bar.high > self.asian_high_morning:
                    self.asian_high_morning = bar.high
                if self.asian_low_morning is None or bar.low < self.asian_low_morning:
                    self.asian_low_morning = bar.low

            # Afternoon range: 08:00–13:00 GMT → used for New York session
            elif 8 <= h <= 13:
                if self.asian_high_afternoon is None or bar.high > self.asian_high_afternoon:
                    self.asian_high_afternoon = bar.high
                if self.asian_low_afternoon is None or bar.low < self.asian_low_afternoon:
                    self.asian_low_afternoon = bar.low

        # reqId 3 — last 50 1-minute bars → pre-seed EMA-50
        #           we keep a rolling window of 50 so only the most recent 50 closes are used
        if reqId == 3:
            self.ema_seed_closes.append(bar.close)
            if len(self.ema_seed_closes) > 50:
                self.ema_seed_closes.pop(0)

    def historicalDataEnd(self, reqId, start, end):
        # reqId 1 — ATR ready once we have 14 daily bars
        if reqId == 1:
            if len(self.daily_tr_list) == 14:
                self.daily_atr = np.mean(self.daily_tr_list)
                print(f"Daily ATR (14-period): {self.daily_atr:.5f}")
            else:
                print(f"Warning: Only {len(self.daily_tr_list)} daily bars received — ATR not ready.")

        # reqId 2 — log both Asian ranges
        if reqId == 2:
            if self.asian_high_morning and self.asian_low_morning:
                morning_size = self.asian_high_morning - self.asian_low_morning
                print(f"Morning Range  (01–07 GMT): High {self.asian_high_morning:.5f}, "
                      f"Low {self.asian_low_morning:.5f}, Size {morning_size:.5f}")
            else:
                print("Warning: No morning Asian range bars found (01:00–07:00 GMT).")

            if self.asian_high_afternoon and self.asian_low_afternoon:
                afternoon_size = self.asian_high_afternoon - self.asian_low_afternoon
                print(f"Afternoon Range (08–13 GMT): High {self.asian_high_afternoon:.5f}, "
                      f"Low {self.asian_low_afternoon:.5f}, Size {afternoon_size:.5f}")
            else:
                print("Warning: No afternoon Asian range bars found (08:00–13:00 GMT).")

        # reqId 3 — seed EMA from last 50 historical 1-minute closes
        if reqId == 3:
            if len(self.ema_seed_closes) == 50:
                self.ema_50        = np.mean(self.ema_seed_closes)
                self.ema_bar_count = 50   # signals _update_ema to skip seeding phase
                print(f"EMA50 pre-seeded from last 50 historical 1m bars: {self.ema_50:.5f}")
            else:
                print(f"Warning: Only {len(self.ema_seed_closes)} bars for EMA seed — "
                      f"EMA will complete seeding from live bars.")

    # ------------------------------------------------------------------ #
    #  2. EMA-50 LIVE UPDATE                                               #
    # ------------------------------------------------------------------ #
    def _update_ema(self, close):
        self.ema_bar_count += 1
        if self.ema_bar_count <= self.ema_span:
            # Seeding phase (only reached if historical pre-seed was incomplete)
            self.ema_seed_closes.append(close)
            if self.ema_bar_count == self.ema_span:
                self.ema_50 = np.mean(self.ema_seed_closes)
                print(f"EMA50 seeded from live bars: {self.ema_50:.5f}")
        else:
            # Exponential update: EMA = close * k + prev_EMA * (1 - k)
            self.ema_50 = close * self.ema_k + self.ema_50 * (1 - self.ema_k)

    # ------------------------------------------------------------------ #
    #  3. LIVE BAR LOGIC                                                   #
    # ------------------------------------------------------------------ #
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        now_gmt = datetime.now().time()

        # Update EMA on every bar regardless of session
        self._update_ema(close)

        is_london = dt_time(8, 0) <= now_gmt <= dt_time(10, 0)
        is_ny     = dt_time(14, 0) <= now_gmt <= dt_time(17, 0)

        if not (is_london or is_ny) or self.in_position:
            return

        # Assign the correct Asian range for the active session
        if is_london:
            active_high = self.asian_high_morning
            active_low  = self.asian_low_morning
        else:  # New York
            active_high = self.asian_high_afternoon
            active_low  = self.asian_low_afternoon

        # Guard: range must exist and be non-zero
        if active_high is None or active_low is None:
            return
        active_size = active_high - active_low
        if active_size == 0:
            return

        # ATR band filter
        if self.daily_atr:
            if not (0.3 * self.daily_atr < active_size < 2.0 * self.daily_atr):
                return

        # Confirmation finished last bar — enter on THIS bar's open
        if self.pending_entry:
            self.execute_trade(open_, active_high, active_low, active_size)
            self.pending_entry = False
            return

        self.check_breakout(close, active_high, active_low)

    # ------------------------------------------------------------------ #
    #  4. BREAKOUT DETECTION & CONFIRMATION                                #
    # ------------------------------------------------------------------ #
    def check_breakout(self, current_close, range_high, range_low):
        # --- First break detection ---
        if self.potential_direction is None:
            if current_close > range_high:
                print("Breakout Long detected — collecting 15 confirmation closes...")
                self.potential_direction = "long"
                self.confirm_closes      = []
            elif current_close < range_low:
                print("Breakout Short detected — collecting 15 confirmation closes...")
                self.potential_direction = "short"
                self.confirm_closes      = []
            return  # first break candle is not counted as a confirmation candle

        # --- Collect the next 15 closes into the confirmation window ---
        if self.potential_direction == "long":
            self.confirm_closes.append(current_close > range_high)
        else:
            self.confirm_closes.append(current_close < range_low)

        # Still building the window
        if len(self.confirm_closes) < self.confirm_minutes:
            return

        # --- Evaluate the completed 15-candle window ---
        counter   = sum(self.confirm_closes)
        precision = counter / self.confirm_minutes

        if precision < 1.0:
            print(f"Confirmation failed ({counter}/{self.confirm_minutes}). Resetting.")
            self._reset_breakout()
            return

        print(f"Breakout CONFIRMED ({counter}/{self.confirm_minutes}). "
              f"Entering on next bar open...")
        self.pending_entry = True

    def _reset_breakout(self):
        self.potential_direction = None
        self.confirm_closes      = []
        self.pending_entry       = False

    # ------------------------------------------------------------------ #
    #  5. TRADE EXECUTION                                                  #
    # ------------------------------------------------------------------ #
    def execute_trade(self, entry_price, range_high, range_low, range_size):
        # EMA filter
        if self.ema_50 is None:
            print("EMA not ready — skipping trade.")
            self._reset_breakout()
            return
        if self.potential_direction == "long" and entry_price < self.ema_50:
            print(f"Trade rejected: Long entry {entry_price:.5f} below EMA50 {self.ema_50:.5f}")
            self._reset_breakout()
            return
        if self.potential_direction == "short" and entry_price > self.ema_50:
            print(f"Trade rejected: Short entry {entry_price:.5f} above EMA50 {self.ema_50:.5f}")
            self._reset_breakout()
            return

        print(f"TRADING SIGNAL: {self.potential_direction} at {entry_price:.5f}")
        self.place_bracket_order(entry_price, range_size)
        self.in_position = True
        self._reset_breakout()

    # ------------------------------------------------------------------ #
    #  6. ORDER PLACEMENT                                                  #
    # ------------------------------------------------------------------ #
    def place_bracket_order(self, entry_price, range_size):
        contract          = Contract()
        contract.symbol   = self.symbol
        contract.secType  = "CASH"
        contract.exchange = "IDEALPRO"
        contract.currency = self.currency

        if self.potential_direction == "long":
            tp     = entry_price + (self.tp_multiplier * range_size)
            sl     = entry_price - (self.sl_multiplier * range_size)
            action = "BUY"
        else:
            tp     = entry_price - (self.tp_multiplier * range_size)
            sl     = entry_price + (self.sl_multiplier * range_size)
            action = "SELL"

        # Parent market order
        parent               = Order()
        parent.orderId       = self.nextId
        parent.action        = action
        parent.orderType     = "MKT"
        parent.totalQuantity = 1000
        parent.transmit      = False

        # Stop Loss
        sl_order               = Order()
        sl_order.parentId      = parent.orderId
        sl_order.action        = "SELL" if action == "BUY" else "BUY"
        sl_order.orderType     = "STP"
        sl_order.auxPrice      = round(sl, 5)
        sl_order.totalQuantity = parent.totalQuantity
        sl_order.transmit      = False

        # Take Profit
        tp_order               = Order()
        tp_order.parentId      = parent.orderId
        tp_order.action        = "SELL" if action == "BUY" else "BUY"
        tp_order.orderType     = "LMT"
        tp_order.lmtPrice      = round(tp, 5)
        tp_order.totalQuantity = parent.totalQuantity
        tp_order.transmit      = True  # transmits the entire bracket

        self.placeOrder(parent.orderId,     contract, parent)
        self.placeOrder(parent.orderId + 1, contract, sl_order)
        self.placeOrder(parent.orderId + 2, contract, tp_order)
        self.nextId += 3


# ------------------------------------------------------------------ #
#  LAUNCH                                                             #
# ------------------------------------------------------------------ #
app = BreakoutBot()
app.connect("127.0.0.1", 7497, clientId=1)
threading.Thread(target=app.run, daemon=True).start()
timeout = 10
while app.nextId is None and timeout > 0:
    time.sleep(0.5)
    timeout -= 0.5

if app.nextId is None:
    print("Failed to connect — check TWS is running and API is enabled.")
    exit()

print(f"Connected. Next valid order ID: {app.nextId}")

eurusd          = Contract()
eurusd.symbol   = "EUR"
eurusd.secType  = "CASH"
eurusd.exchange = "IDEALPRO"
eurusd.currency = "USD"

# reqId 1 — 30 days of daily bars → 14-period ATR (full day High-Low per bar)
app.reqHistoricalData(1, eurusd, "", "30 D", "1 day", "MIDPOINT", 1, 1, False, [])

# reqId 2 — today's 1-minute bars → morning (01-07) and afternoon (08-13) Asian ranges
app.reqHistoricalData(2, eurusd, "", "1 D", "1 min", "MIDPOINT", 1, 1, False, [])

# reqId 3 — last 50 1-minute bars → pre-seed EMA-50 before live stream starts
app.reqHistoricalData(3, eurusd, "", "1 D", "1 min", "MIDPOINT", 1, 1, False, [])

# Live 5-second bars → drives all session logic and EMA updates
app.reqRealTimeBars(4, eurusd, 5, "MIDPOINT", True, [])

while True:
    time.sleep(1)