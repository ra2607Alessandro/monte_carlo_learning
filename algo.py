from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time
import time

class BreakoutBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextId = None
        
        # Strategy Parameters
        self.symbol = "EUR"
        self.currency = "USD"
        self.confirm_minutes = 15
        self.tp_multiplier = 2.0
        self.sl_multiplier = 0.5
        
        # State Data
        self.asian_high = None
        self.asian_low = None
        self.asian_range_size = None
        self.daily_atr = None
        self.ema_50 = None
        self.live_bars = [] # Stores recent 1m bars for EMA
        
        # State Machine
        self.in_position = False
        self.confirm_counter = 0
        self.potential_direction = None

    def nextValidId(self, orderId):
        self.nextId = orderId

    def error(self, reqId, errorCode, errorString, contract):
        if errorCode not in [2104, 2106, 2158]: # Filter harmless connection messages
            print(f"Error {errorCode}: {errorString}")

    # --- 1. DATA COLLECTION ---
    def historicalData(self, reqId, bar):
        # reqId 1: Daily data for ATR
        # reqId 2: 1m data for Asian Range
        if reqId == 1:
            # Simple ATR calculation logic from your file
            tr = bar.high - bar.low
            self.daily_atr = tr # simplified for this example; usually rolling mean of 14
        if reqId == 2:
            if self.asian_high is None or bar.high > self.asian_high: self.asian_high = bar.high
            if self.asian_low is None or bar.low < self.asian_low: self.asian_low = bar.low

    def historicalDataEnd(self, reqId, start, end):
        if reqId == 2:
            self.asian_range_size = self.asian_high - self.asian_low
            print(f"Range Calculated: High {self.asian_high}, Low {self.asian_low}, Size {self.asian_range_size}")

    # --- 2. LIVE BAR LOGIC ---
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        # Logic executes every 5 seconds or 1 minute bar
        now_gmt = datetime.utcnow().time()
        
        # Calculate EMA50 on the fly
        self.live_bars.append(close)
        if len(self.live_bars) > 50:
            self.live_bars.pop(0)
            self.ema_50 = np.mean(self.live_bars) # Simplified EMA

        # Only trade if filters are met (ATR check)
        if self.daily_atr and self.asian_range_size:
            if not (0.3 * self.daily_atr < self.asian_range_size < 2.0 * self.daily_atr):
                return # Range is "Outside ATR band" - No Trade

        # SESSION CHECK: London (08:00-10:00 GMT) or NY (14:00-17:00 GMT)
        is_london = dt_time(8, 0) <= now_gmt <= dt_time(10, 0)
        is_ny = dt_time(14, 0) <= now_gmt <= dt_time(17, 0)

        if (is_london or is_ny) and not self.in_position:
            self.check_breakout(close)

    def check_breakout(self, current_close):
        # BREAKOUT DETECTION
        if current_close > self.asian_high and self.potential_direction is None:
            print("Breakout Long Detected. Starting 15m confirmation...")
            self.potential_direction = "long"
            self.confirm_counter = 0
        elif current_close < self.asian_low and self.potential_direction is None:
            print("Breakout Short Detected. Starting 15m confirmation...")
            self.potential_direction = "short"
            self.confirm_counter = 0

        # CONFIRMATION LOGIC (The 15 candles check)
        if self.potential_direction == "long":
            if current_close > self.asian_high:
                self.confirm_counter += 1
            else:
                self.potential_direction = None # Reset if a candle closes back in range
        
        if self.potential_direction == "short":
            if current_close < self.asian_low:
                self.confirm_counter += 1
            else:
                self.potential_direction = None

        # EXECUTION (After 15 minutes of staying outside range)
        if self.confirm_counter >= self.confirm_minutes:
            self.execute_trade(current_close)

    def execute_trade(self, entry_price):
        # EMA FILTER check
        if self.potential_direction == "long" and entry_price < self.ema_50:
            print("Trade rejected: Entry below EMA50")
            self.potential_direction = None
            return
        if self.potential_direction == "short" and entry_price > self.ema_50:
            print("Trade rejected: Entry above EMA50")
            self.potential_direction = None
            return

        print(f"TRADING SIGNAL: {self.potential_direction} at {entry_price}")
        self.place_bracket_order(entry_price)
        self.in_position = True

    def place_bracket_order(self, entry_price):
        contract = Contract()
        contract.symbol = self.symbol
        contract.secType = "CASH" # Forex
        contract.exchange = "IDEALPRO"
        contract.currency = self.currency

        # Calculate TP/SL from your multipliers
        if self.potential_direction == "long":
            tp = entry_price + (self.tp_multiplier * self.asian_range_size)
            sl = entry_price - (self.sl_multiplier * self.asian_range_size)
            action = "BUY"
        else:
            tp = entry_price - (self.tp_multiplier * self.asian_range_size)
            sl = entry_price + (self.sl_multiplier * self.asian_range_size)
            action = "SELL"

        # Main Order
        parent = Order()
        parent.orderId = self.nextId
        parent.action = action
        parent.orderType = "MKT"
        parent.totalQuantity = 20000 # 20k units
        parent.transmit = False

        # Stop Loss
        sl_order = Order()
        sl_order.parentId = parent.orderId
        sl_order.action = "SELL" if action == "BUY" else "BUY"
        sl_order.orderType = "STP"
        sl_order.auxPrice = round(sl, 5)
        sl_order.totalQuantity = parent.totalQuantity
        sl_order.transmit = False

        # Take Profit
        tp_order = Order()
        tp_order.parentId = parent.orderId
        tp_order.action = "SELL" if action == "BUY" else "BUY"
        tp_order.orderType = "LMT"
        tp_order.lmtPrice = round(tp, 5)
        tp_order.totalQuantity = parent.totalQuantity
        tp_order.transmit = True # Finalize bracket

        self.placeOrder(parent.orderId, contract, parent)
        self.placeOrder(parent.orderId + 1, contract, sl_order)
        self.placeOrder(parent.orderId + 2, contract, tp_order)
        self.nextId += 3

# --- Launch Bot ---
app = BreakoutBot()
app.connect("127.0.0.1", 7497, clientId=1)
threading.Thread(target=app.run, daemon=True).start()
time.sleep(2)

# Initialization: Get Asian Range (1:00 to 7:00 GMT today) and Daily ATR
# In a real scenario, you'd calculate these every morning.
eurusd = Contract()
eurusd.symbol = "EUR"
eurusd.secType = "CASH"
eurusd.exchange = "IDEALPRO"
eurusd.currency = "USD"

# Requesting Range for today's Asian Session
app.reqHistoricalData(2, eurusd, "", "1 D", "1 min", "MIDPOINT", 1, 1, False, [])
# Requesting Daily data for ATR filter
app.reqHistoricalData(1, eurusd, "", "30 D", "1 day", "MIDPOINT", 1, 1, False, [])
# Start Live Stream
app.reqRealTimeBars(3, eurusd, 5, "MIDPOINT", True, [])

while True:
    time.sleep(1)