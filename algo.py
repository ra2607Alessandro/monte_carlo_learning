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

        # --- Strategy Parameters ---
        self.symbol = "EUR"
        self.currency = "USD"
        self.confirm_minutes = 15
        self.tp_multiplier = 2.0
        self.sl_multiplier = 0.8 # Matches your backtest (1).py logic

        # --- Quantity
        self.quantity = 1000

        # --- Asian Ranges (Dynamic Max/Min) ---
        self.asian_high_morning = -float('inf')
        self.asian_low_morning = float('inf')
        self.asian_high_afternoon = -float('inf')
        self.asian_low_afternoon = float('inf')

        # Flags to prevent double reporting
        self.morning_printed = False
        self.afternoon_printed = False

        # --- Indicators ---
        self.daily_tr_list = []
        self.daily_atr = None
        self.ema_50 = None
        self.ema_seed_closes = []
        self.ema_k = 2 / (50 + 1)

        # --- State Machine ---
        self.in_position = False
        self.potential_direction = None
        self.confirm_counter = 0 
        self.last_minute = None

    # ------------------------------------------------------------------ #
    #  API HANDSHAKE & DATA SYNC                                         #
    # ------------------------------------------------------------------ #
    def nextValidId(self, orderId):
        self.nextId = orderId
        self.reqMarketDataType(3) # Use Delayed data if Live is not active
        print(f"CONNECTED. Handshake Successful. Next Order ID: {self.nextId}")

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson="", contract=None):
        if errorCode not in [2104, 2106, 2158]:
            print(f"IBKR Msg {errorCode}: {errorString}")

    def historicalData(self, reqId, bar):
        if reqId == 1: # ATR Logic
            self.daily_tr_list.append(bar.high - bar.low)
        if reqId == 2: # Asian Range Sync
            dt = datetime.strptime(bar.date.split()[0] + " " + bar.date.split()[1], "%Y%m%d %H:%M:%S")
            h = dt.hour
            if 1 <= h <= 7:
                self.asian_high_morning = max(self.asian_high_morning, bar.high)
                self.asian_low_morning = min(self.asian_low_morning, bar.low)
            elif 8 <= h <= 13:
                self.asian_high_afternoon = max(self.asian_high_afternoon, bar.high)
                self.asian_low_afternoon = min(self.asian_low_afternoon, bar.low)
        if reqId == 3: # EMA 50 Seed
            self.ema_seed_closes.append(bar.close)

    def historicalDataEnd(self, reqId, start, end):
        if reqId == 1: 
            self.daily_atr = np.mean(self.daily_tr_list[-14:])
            print(f"ATR Ready: {self.daily_atr:.5f}")
        if reqId == 3: 
            self.ema_50 = np.mean(self.ema_seed_closes[-50:])
            print(f"EMA Ready: {self.ema_50:.5f}")
        if reqId == 2:
            print("Asian Range Initial Sync Complete.")
            now_h = datetime.now(timezone.utc).hour
            if now_h >= 8:
                self.report_session("STARTUP AUDIT: MORNING", self.asian_high_morning, self.asian_low_morning)
                self.morning_printed = True
            if now_h >= 14:
                self.report_session("STARTUP AUDIT: AFTERNOON", self.asian_high_afternoon, self.asian_low_afternoon)
                self.afternoon_printed = True

    # ------------------------------------------------------------------ #
    #  LIVE EXECUTION ENGINE                                             #
    # ------------------------------------------------------------------ #
    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 1: # 1 = BID Price
            self.on_price_update(price)

    def on_price_update(self, price):
        now_utc = datetime.now(timezone.utc)
        h, m = now_utc.hour, now_utc.minute

        # A. UPDATE EMA Live
        if self.ema_50 is not None:
            self.ema_50 = (price * self.ema_k) + (self.ema_50 * (1 - self.ema_k))

        # B. UPDATE RANGES Live (Prevents "Too Little" bug)
        if 1 <= h <= 7:
            self.asian_high_morning = max(self.asian_high_morning, price)
            self.asian_low_morning = min(self.asian_low_morning, price)
            self.morning_printed = False 
        elif h == 8 and not self.morning_printed:
            self.report_session("MORNING", f' High: {self.asian_high_morning}', f' Low: {self.asian_low_morning}')
            self.morning_printed = True

        if 8 <= h <= 13:
            self.asian_high_afternoon = max(self.asian_high_afternoon, price)
            self.asian_low_afternoon = min(self.asian_low_afternoon, price)
            self.afternoon_printed = False
        elif h == 14 and not self.afternoon_printed:
            self.report_session("AFTERNOON",f' High: {self.asian_high_afternoon}', f' Low: {self.asian_low_afternoon}')
            self.afternoon_printed = True

        # C. SESSION SCANNING
        now_time = now_utc.time()
        is_london = dt_time(8, 0) <= now_time <= dt_time(10, 0)
        is_ny = dt_time(14, 0) <= now_time <= dt_time(17, 0)

        if self.in_position or not (is_london or is_ny):
            return

        active_h = self.asian_high_morning if is_london else self.asian_high_afternoon
        active_l = self.asian_low_morning if is_london else self.asian_low_afternoon
        
        if active_h == -float('inf'): return
        active_size = active_h - active_l

        # Volatility check
        if self.daily_atr and not (0.3 * self.daily_atr < active_size < 2.0 * self.daily_atr):
            return

        # D. CONFIRMATION LOGIC
        if self.last_minute != m:
            self.last_minute = m
            if price > active_h:
                self.confirm_counter = (self.confirm_counter + 1) if self.potential_direction == "long" else 1
                self.potential_direction = "long"
            elif price < active_l:
                self.confirm_counter = (self.confirm_counter + 1) if self.potential_direction == "short" else 1
                self.potential_direction = "short"
            else:
                self.confirm_counter = 0; self.potential_direction = None

            # F. FINAL ENTRY CHECK
            if self.confirm_counter >= self.confirm_minutes:
                if (self.potential_direction == "long" and price > self.ema_50) or \
                   (self.potential_direction == "short" and price < self.ema_50):
                    self.place_bracket_order(price, active_size)
                    self.in_position = True

    # ------------------------------------------------------------------ #
    #  ORDER PLACEMENT                                                   #
    # ------------------------------------------------------------------ #
    def place_bracket_order(self, entry_price, range_size):
        contract = Contract()
        contract.symbol = "EUR"; contract.secType = "CASH"; contract.exchange = "IDEALPRO"; contract.currency = "USD"
        
        action = "BUY" if self.potential_direction == "long" else "SELL"
        rev_action = "SELL" if action == "BUY" else "BUY"
        
        tp = entry_price + (self.tp_multiplier * range_size) if action == "BUY" else entry_price - (self.tp_multiplier * range_size)
        sl = entry_price - (self.sl_multiplier * range_size) if action == "BUY" else entry_price + (self.sl_multiplier * range_size)

        # 1. Parent MKT Order
        parent = Order()
        parent.orderId = self.nextId
        parent.action = action; parent.orderType = "MKT"; parent.totalQuantity = self.quantity; parent.transmit = False

        # 2. Stop Loss Order
        sl_order = Order()
        sl_order.orderId = parent.orderId + 1; sl_order.parentId = parent.orderId
        sl_order.action = rev_action; sl_order.orderType = "STP"; sl_order.auxPrice = round(sl, 5); sl_order.totalQuantity = self.quantity; sl_order.transmit = False

        # 3. Take Profit Order
        tp_order = Order()
        tp_order.orderId = parent.orderId + 2; tp_order.parentId = parent.orderId
        tp_order.action = rev_action; tp_order.orderType = "LMT"; tp_order.lmtPrice = round(tp, 5); tp_order.totalQuantity = 20000; tp_order.transmit = True

        self.placeOrder(parent.orderId, contract, parent)
        self.placeOrder(sl_order.orderId, contract, sl_order)
        self.placeOrder(tp_order.orderId, contract, tp_order)
        self.nextId += 3
        print(f"!!! TRADING SIGNAL: Opening {self.potential_direction} @ {entry_price:.5f} (SL: {sl:.5f}, TP: {tp:.5f})")

    def report_session(self, name, h, l):
        print(f"\nAUDIT [{name}] -> Final High: {h:.5f}, Final Low: {l:.5f}, ATR: {self.daily_atr:.5f}\n")

# --- START ---
app = BreakoutBot()
app.connect("127.0.0.1", 7497, clientId=1)
threading.Thread(target=app.run, daemon=True).start()
time.sleep(2)

eurusd = Contract()
eurusd.symbol = "EUR"; eurusd.secType = "CASH"; eurusd.exchange = "IDEALPRO"; eurusd.currency = "USD"

app.reqHistoricalData(1, eurusd, "", "30 D", "1 day", "BID", 1, 1, False, [])
app.reqHistoricalData(2, eurusd, "", "1 D", "1 min", "BID", 1, 1, False, [])
app.reqHistoricalData(3, eurusd, "", "1 D", "1 min", "BID", 1, 1, False, [])
app.reqMktData(4, eurusd, "", False, False, [])

while True:
    time.sleep(1)