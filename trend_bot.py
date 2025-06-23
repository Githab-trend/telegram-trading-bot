import requests
import pandas as pd
import numpy as np
import time
import schedule
import telebot

BOT_TOKEN = "7954820177:AAGyODLYEdPqGY6_y0Cgh0QE5Ujjkb8V_P4"
CHAT_ID = "-1002794962661"

bot = telebot.TeleBot(BOT_TOKEN)

def get_price_data(symbol: str, interval='5m', limit=50):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close Time', 'Quote Asset Volume', 'Number of Trades',
            'Taker Buy Base', 'Taker Buy Quote', 'Ignore'
        ])
        df['Close'] = df['Close'].astype(float)
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None

def check_trend(symbol):
    df = get_price_data(symbol)
    if df is None:
        return

    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()

    trend = None

    if (
        df['MA5'].iloc[-2] < df['MA20'].iloc[-2]
        and df['MA5'].iloc[-1] > df['MA20'].iloc[-1]
    ):
        trend = "🟢 Buy signal"
    elif (
        df['MA5'].iloc[-2] > df['MA20'].iloc[-2]
        and df['MA5'].iloc[-1] < df['MA20'].iloc[-1]
    ):
        trend = "🔴 Sell signal"

    if trend:
        message = f"{trend} detected on {symbol}.\nSuggested duration: 15 minutes."
        bot.send_message(CHAT_ID, message)
        print(message)

    print(df.tail())  # Debug info

def job():
    print("🔍 Checking trend...")
    check_trend("BTCUSDT")
    check_trend("ETHUSDT")

bot.send_message(CHAT_ID, "✅ Bot started. Sending trend signals every 5 minutes...")

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)