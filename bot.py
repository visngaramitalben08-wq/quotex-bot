import pandas as pd
import requests
import time
from datetime import datetime

TOKEN = "8738482142:AAFpajOqPqnceqS9wc91ai-5rc0Xlfvgw-A"
CHAT_ID = "6656459688"

# TELEGRAM SEND
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

# GET EURUSD DATA
def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=EURUSDT&interval=1m&limit=150"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df = df.iloc[:,0:5]
    df.columns = ["time","open","high","low","close"]
    df = df.astype(float)
    return df

# INDICATORS
def indicators(df):
    df["ema9"] = df["close"].ewm(span=9).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    # RSI
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df

# SIGNAL LOGIC
def check_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None
    confidence = 0

    # BUY
    if (last["close"] > last["ema50"] and
        prev["low"] < prev["ema9"] and
        last["close"] > last["ema9"] and
        last["rsi"] > 50):
        signal = "BUY 🟢"
        confidence = 80

    # SELL
    if (last["close"] < last["ema50"] and
        prev["high"] > prev["ema9"] and
        last["close"] < last["ema9"] and
        last["rsi"] < 50):
        signal = "SELL 🔴"
        confidence = 80

    return signal, confidence

# FORMAT MESSAGE
def format_msg(signal, confidence):
    time_now = datetime.now().strftime("%H:%M:%S")
    msg = f"""
🚨 QUOTEX SIGNAL 🚨

PAIR: EURUSD
TIMEFRAME: 1 MINUTE
SIGNAL: {signal}

ENTRY TIME: {time_now}
EXPIRY: 1 MIN

CONFIDENCE: {confidence}%

⚠️ Use Proper Risk Management
"""
    return msg

# MAIN LOOP
while True:
    df = get_data()
    df = indicators(df)
    signal, confidence = check_signal(df)

    if signal:
        message = format_msg(signal, confidence)
        send_telegram(message)

    time.sleep(60)