
import ccxt
import time
import streamlit as st
import pandas as pd
from datetime import datetime
from ta.volatility import BollingerBands

# إعداد الواجهة
st.set_page_config(page_title="THE1000X Bot", layout="wide")
st.title("🚀 واجهة مراقبة البوت THE1000X")
st.markdown("### ✅ معلومات السوق الحية")

# إعدادات
symbol = 'BTC/USDT:USDT'

API_KEY = "75707130-0c51-4ee2-a260-0267a7153737"
SECRET_KEY = "C59D6F8A8447EA40AB70E45585FAB7A3"
PASSPHRASE = "THE1000X@BTC100x"

# الاتصال بـ OKX
exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'password': PASSPHRASE,
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

# جلب السعر اللحظي و Bollinger Bands
def get_market_data():
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=21)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_mid'] = bb.bollinger_mavg()
        df['bb_bbl'] = bb.bollinger_lband()
        df['bb_bbh'] = bb.bollinger_hband()
        return df
    except Exception as e:
        st.error(f"فشل في جلب البيانات: {e}")
        return None

# عرض البيانات
df = get_market_data()
if df is not None:
    price = df['close'].iloc[-1]
    lb = round(df['bb_bbl'].iloc[-1], 2)
    ub = round(df['bb_bbh'].iloc[-1], 2)
    mid = round(df['bb_mid'].iloc[-1], 2)

    st.metric("السعر الحالي", f"${price}")
    st.metric("Upper Band", f"${ub}")
    st.metric("Lower Band", f"${lb}")
    st.metric("Mid Band", f"${mid}")
    st.line_chart(df['close'])
