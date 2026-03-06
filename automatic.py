from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import numpy as np
from datetime import datetime, timezone, time as dt_time
import time

class BreakoutBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextId = None
        self.symbol = "EUR"
        self.currency = "USD"
        
        # Ranges & Indicators
        self.asian_high_morning = -float('inf')
        self.asian_low_morning = float('inf')
        self.asian_high_afternoon = -float('inf')
        self.asian_low_afternoon = float('inf')
        self.daily_atr = None
        self.ema_50 = None
        self.ema_seed_closes = []
        self.ema_k = 2 / (50 + 1)

        # Execution State
        self.in_position = False
        self.confirm_counter = 0
        self.potential_direction = None
        self.last_minute = None # Track minute changes for confirmation

    def nextValidId(self, orderId):
        self.nextId = orderId
        # Market Data Type 3 = Delayed, Type 4 = Delayed-Frozen
        # We set it to 3 to catch whatever "Live-ish" data IBKR is allowing
        self.reqMarketDataType(3) 
        print(f"Handshake Successful. Bot is monitoring BID ticks. ID: {self.nextId}")

    # ------------------------------------------------------------------ #
    #  THE NEW LIVE STREAM (Replaces RealTimeBars)                       #
    # ------------------------------------------------------------------ #
    def tickPrice(self, reqId, tickType, price, attrib):
        # tickType 1 = BID price. This is what your backtest uses.
        if tickType == 1: 
            self.on_price_update(price)

    def on_price_update(self, price):
        """This replaces the logic that was inside RealTimeBars"""
        now_utc = datetime.now(timezone.utc)
        current_minute = now_utc.minute
        h = now_utc.hour

        # 1. UPDATE RANGES DYNAMICALLY
        if 1 <= h <= 7:
            self.asian_high_morning = max(self.asian_high_morning, price)
            self.asian_low_morning = min(self.asian_low_morning, price)
        elif 8 <= h <= 13:
            self.asian_high_afternoon = max(self.asian_high_afternoon, price)
            self.asian_low_afternoon = min(self.asian_low_afternoon, price)

        # 2. SESSION & EXECUTION LOGIC
        is_london = dt_time(8, 0) <= now_utc.time() <= dt_time(10, 0)
        is_ny = dt_time(14, 0) <= now_utc.time() <= dt_time(17, 0)

        if self.in_position or not (is_london or is_ny):
            return

        active_h = self.asian_high_morning if is_london else self.asian_high_afternoon
        active_l = self.asian_low_morning if is_london else self.asian_low_afternoon

        # 3. CONFIRMATION LOGIC (Minute-by-Minute)
        if self.last_minute != current_minute:
            self.last_minute = current_minute
            
            # Check Breakout
            if price > active_h:
                if self.potential_direction == "long": self.confirm_counter += 1
                else: self.potential_direction = "long"; self.confirm_counter = 1
            elif price < active_l:
                if self.potential_direction == "short": self.confirm_counter += 1
                else: self.potential_direction = "short"; self.confirm_counter = 1
            else:
                self.confirm_counter = 0
                self.potential_direction = None

            # 4. EXECUTION
            if self.confirm_counter >= 15:
                # Add your EMA check here
                if (self.potential_direction == "long" and price > self.ema_50) or \
                   (self.potential_direction == "short" and price < self.ema_50):
                    self.place_bracket_order(price, (active_h - active_l))
                    self.in_position = True

    # [HistoricalData, historicalDataEnd, place_bracket_order functions remain the same]

# --- EXECUTION ---
app = BreakoutBot()
app.connect("127.0.0.1", 7497, clientId=1)
threading.Thread(target=app.run, daemon=True).start()
time.sleep(2)

eurusd = Contract()
eurusd.symbol = "EUR"; eurusd.secType = "CASH"; eurusd.exchange = "IDEALPRO"; eurusd.currency = "USD"

# 1. Sync ATR and EMA
app.reqHistoricalData(1, eurusd, "", "30 D", "1 day", "BID", 1, 1, False, [])
app.reqHistoricalData(3, eurusd, "", "1 D", "1 min", "BID", 1, 1, False, [])

# 2. START THE LIVE TICK STREAM (Works on Paper accounts)
app.reqMktData(4, eurusd, "", False, False, [])

while True:
    time.sleep(1)