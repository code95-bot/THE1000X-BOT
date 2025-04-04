# THE1000X_LONG&SHORT - النسخة النهائية المعدّلة ✅
# ✨ بوت تداول عقود آجلة (Isolated / Limit Order) باستراتيجية تعزيز تدريجية

import ccxt
import time
import pandas as pd
from ta.volatility import BollingerBands
from datetime import datetime, date
import requests
from collections import defaultdict

# 🛡️ مفاتيح API وتليجرام
API_KEY = "75707130-0c51-4ee2-a260-0267a7153737"
SECRET_KEY = "C59D6F8A8447EA40AB70E45585FAB7A3"
PASSPHRASE = "THE1000X@BTC100x"
TELEGRAM_TOKEN = '7753380104:AAGF9sFWUb6Ak8VPlDRrnhQafx5K0FMJyk4'
TELEGRAM_CHAT_ID = '5032206239'

# ⚙️ إعدادات التداول
symbol = 'BTC/USDT:USDT'
leverage = 100
order_refresh_seconds = 30
rise_drop_percent = 50

# 💰 كميات الصفقات
amounts = [round(0.01 * (2 ** i), 4) for i in range(10)]

# 🔗 الاتصال بـ OKX
exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'password': PASSPHRASE,
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

# 📩 تليجرام
def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        print("⚠️ فشل إرسال الرسالة")

# 🔢 عداد الصفقات
trade_counter = defaultdict(int)
today_str = date.today().isoformat()
def get_trade_count(trade_type):
    key = f"{today_str}_{trade_type}"
    trade_counter[key] += 1
    return f"{trade_counter[key]:02d}"

# 📊 مستويات التعزيز
levels = [0.001, 0.002, 0.0039, 0.0078, 0.0156, 0.0313, 0.0625, 0.125, 0.25, 0.5]
def get_entry_price(direction, first_entry, index):
    pct = levels[index]
    factor = pct * rise_drop_percent / 100
    return round(first_entry * (1 - factor), 2) if direction == 'LONG' else round(first_entry * (1 + factor), 2)

# ❌ إلغاء أوامر الدخول المفتوحة
def cancel_old_entry_orders():
    orders = exchange.fetch_open_orders(symbol)
    for o in orders:
        if o['type'] == 'limit' and o['status'] == 'open':
            side = o['side']
            pos_side = o['info'].get('posSide', '')
            if (side == 'buy' and pos_side == 'long') or (side == 'sell' and pos_side == 'short'):
                try:
                    exchange.cancel_order(o['id'], symbol)
                except:
                    pass

# ♻️ المتغيرات
executed_long = [False] * 10
executed_short = [False] * 10
open_orders_long = [None] * 10
open_orders_short = [None] * 10
entry_prices_long = [None] * 10
entry_prices_short = [None] * 10
tp_order_long = None
tp_order_short = None
first_long_executed_price = None
first_short_executed_price = None

print("🚀 البوت يعمل...")
cancel_old_entry_orders()

while True:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=21)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_mid'] = bb.bollinger_mavg()
        df['bb_bbl'] = bb.bollinger_lband()
        df['bb_bbh'] = bb.bollinger_hband()
        price = df['close'].iloc[-1]
        lb = round(df['bb_bbl'].iloc[-1], 2)
        ub = round(df['bb_bbh'].iloc[-1], 2)
        mid = round(df['bb_mid'].iloc[-1], 2)

        print(f"\n🕒 {datetime.now().strftime('%H:%M:%S')} | Price: {price} | LB: {lb} | MID: {mid} | UB: {ub}")

        # ========== LONG STRATEGY ==========
        for i in range(10):
            entry_price = lb if i == 0 or first_long_executed_price is None else get_entry_price('LONG', first_long_executed_price, i)

            if not executed_long[i]:
                if open_orders_long[i]:
                    status = exchange.fetch_order(open_orders_long[i], symbol)
                    if status['status'] != 'closed':
                        try:
                            exchange.cancel_order(open_orders_long[i], symbol)
                        except:
                            pass
                try:
                    order = exchange.create_order(symbol, 'limit', 'buy', amounts[i], entry_price,
                                                  {'posSide': 'long', 'tdMode': 'isolated'})
                    open_orders_long[i] = order['id']
                    entry_prices_long[i] = entry_price
                    print(f"🟢 Long_Open_Trade_{i+1:02} @ {entry_price}")
                except Exception as e:
                    print(f"❌ Long_Open_Trade_{i+1:02} Error: {e}")

            if open_orders_long[i]:
                status = exchange.fetch_order(open_orders_long[i], symbol)
                if status['status'] == 'closed' and not executed_long[i]:
                    executed_long[i] = True
                    avg = float(status['average'])
                    send_telegram(f"🟢 Long_Open_Trade_{i+1:02} Executed @ {avg}")
                    if i == 0:
                        first_long_executed_price = avg
                    try:
                        tp_price = mid if i == 0 else entry_prices_long[i - 1]
                        tp = exchange.create_order(symbol, 'limit', 'sell', amounts[i], tp_price,
                                                   {'posSide': 'long', 'tdMode': 'isolated'})
                        if i == 0:
                            tp_order_long = tp['id']
                        print(f"📤 Long_Close_Trade_{i+1:02} @ {tp_price}")
                    except:
                        print(f"TP Long_Close_Trade_{i+1:02} Error")
                if not executed_long[i]:
                    break

        if executed_long[0] and tp_order_long:
            try:
                status = exchange.fetch_order(tp_order_long, symbol)
                if status['status'] == 'closed':
                    print("✅ تم غلق Long TP 01 → إعادة تشغيل LONG")
                    for j in range(1, 10):
                        if open_orders_long[j] and not executed_long[j]:
                            try:
                                exchange.cancel_order(open_orders_long[j], symbol)
                                print(f"❌ تم إلغاء تعزيز LONG {j+1}")
                            except:
                                pass
                        executed_long[j] = False
                        open_orders_long[j] = None
                        entry_prices_long[j] = None
                    executed_long[0] = False
                    open_orders_long[0] = None
                    entry_prices_long[0] = None
                    tp_order_long = None
                    first_long_executed_price = None
                else:
                    exchange.cancel_order(tp_order_long, symbol)
                    new_tp = exchange.create_order(symbol, 'limit', 'sell', amounts[0], mid,
                                                   {'posSide': 'long', 'tdMode': 'isolated'})
                    tp_order_long = new_tp['id']
                    print(f"♻️ تحديث Long_Close_Trade_01 @ {mid}")
            except:
                print("⚠️ تحديث TP LONG 01 Error")

        # ========== SHORT STRATEGY ==========
        for i in range(10):
            entry_price = ub if i == 0 or first_short_executed_price is None else get_entry_price('SHORT', first_short_executed_price, i)

            if not executed_short[i]:
                if open_orders_short[i]:
                    status = exchange.fetch_order(open_orders_short[i], symbol)
                    if status['status'] != 'closed':
                        try:
                            exchange.cancel_order(open_orders_short[i], symbol)
                        except:
                            pass
                try:
                    order = exchange.create_order(symbol, 'limit', 'sell', amounts[i], entry_price,
                                                  {'posSide': 'short', 'tdMode': 'isolated'})
                    open_orders_short[i] = order['id']
                    entry_prices_short[i] = entry_price
                    print(f"🔴 Short_Open_Trade_{i+1:02} @ {entry_price}")
                except Exception as e:
                    print(f"❌ Short_Open_Trade_{i+1:02} Error: {e}")

            if open_orders_short[i]:
                status = exchange.fetch_order(open_orders_short[i], symbol)
                if status['status'] == 'closed' and not executed_short[i]:
                    executed_short[i] = True
                    avg = float(status['average'])
                    send_telegram(f"🔴 Short_Open_Trade_{i+1:02} Executed @ {avg}")
                    if i == 0:
                        first_short_executed_price = avg
                    try:
                        tp_price = mid if i == 0 else entry_prices_short[i - 1]
                        tp = exchange.create_order(symbol, 'limit', 'buy', amounts[i], tp_price,
                                                   {'posSide': 'short', 'tdMode': 'isolated'})
                        if i == 0:
                            tp_order_short = tp['id']
                        print(f"📥 Short_Close_Trade_{i+1:02} @ {tp_price}")
                    except:
                        print(f"TP Short_Close_Trade_{i+1:02} Error")
                if not executed_short[i]:
                    break

        if executed_short[0] and tp_order_short:
            try:
                status = exchange.fetch_order(tp_order_short, symbol)
                if status['status'] == 'closed':
                    print("✅ تم غلق Short TP 01 → إعادة تشغيل SHORT")
                    for j in range(1, 10):
                        if open_orders_short[j] and not executed_short[j]:
                            try:
                                exchange.cancel_order(open_orders_short[j], symbol)
                                print(f"❌ تم إلغاء تعزيز SHORT {j+1}")
                            except:
                                pass
                        executed_short[j] = False
                        open_orders_short[j] = None
                        entry_prices_short[j] = None
                    executed_short[0] = False
                    open_orders_short[0] = None
                    entry_prices_short[0] = None
                    tp_order_short = None
                    first_short_executed_price = None
                else:
                    exchange.cancel_order(tp_order_short, symbol)
                    new_tp = exchange.create_order(symbol, 'limit', 'buy', amounts[0], mid,
                                                   {'posSide': 'short', 'tdMode': 'isolated'})
                    tp_order_short = new_tp['id']
                    print(f"♻️ تحديث Short_Close_Trade_01 @ {mid}")
            except:
                print("⚠️ تحديث TP SHORT 01 Error")

    except Exception as e:
        print(f"❌ خطأ عام: {e}")

    time.sleep(order_refresh_seconds)
