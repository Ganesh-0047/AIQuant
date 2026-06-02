import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from fastapi import Request
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
from ta.momentum import RSIIndicator

app = FastAPI()
#PAPER TRADING DATA
balance = 10000
position = None
entry_price = 0
trade_history = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "message": "Backend Running"
    }


@app.get("/btc-price")
def btc_price():

    return {
        "bitcoin_price": 77291
    }


@app.get("/btc-rsi")
def btc_rsi():

    return {
        "rsi": 56.08,
        "signal": "HOLD"
    }
@app.get("/paper-trade")
def paper_trade():

    global balance
    global position
    global entry_price
    global trade_history

    # Get RSI Data

    btc = yf.Ticker("BTC-USD")

    hist = btc.history(period="7d", interval="15m")

    closes = hist["Close"].dropna().tolist()

    if len(closes) == 0:
        return {
            "error": "No price data received"
        }

    current_price = closes[-1]

    df = pd.DataFrame(closes, columns=["close"])

    rsi_indicator = RSIIndicator(close=df["close"])

    df["rsi"] = rsi_indicator.rsi()

    latest_rsi = df["rsi"].iloc[-1]

    action = "HOLD"

    # BUY CONDITION

    if latest_rsi < 30 and position is None:

        position = "BUY"

        entry_price = current_price

        action = "BUY"
        send_telegram_message(
    f"🟢 BUY SIGNAL\nBTC Price: ${current_price}\nRSI: {latest_rsi}"
)

        trade_history.append({
            "type": "BUY",
            "price": current_price
        })


    # SELL CONDITION

    elif latest_rsi > 70 and position == "BUY":

        profit = current_price - entry_price

        balance += profit

        action = "SELL"
        send_telegram_message(
    f"🔴 SELL SIGNAL\nBTC Price: ${current_price}\nRSI: {latest_rsi}"
)

        trade_history.append({
            "type": "SELL",
            "price": current_price,
            "profit": round(profit, 2)
        })

        position = None


    return {

        "balance": round(balance, 2),

        "position": position,

        "btc_price": current_price,

        "rsi": round(float(latest_rsi), 2),

        "action": action,

        "trade_history": trade_history[-5:]
    }
@app.get("/ai-sentiment")
def ai_sentiment():

    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100"

    response = requests.get(url)

    data = response.json()

    closes = []

    for candle in data:

        closes.append(float(candle[4]))

    df = pd.DataFrame(closes, columns=["close"])

    rsi_indicator = RSIIndicator(close=df["close"])

    df["rsi"] = rsi_indicator.rsi()

    latest_rsi = df["rsi"].iloc[-1]


    mood = "NEUTRAL"

    confidence = 50


    if latest_rsi < 30:

        mood = "BULLISH"

        confidence = 82


    elif latest_rsi > 70:

        mood = "BEARISH"

        confidence = 87


    return {

        "mood": mood,

        "confidence": confidence

    }
@app.get("/performance")
def performance():

    total_trades = len(trade_history)

    profitable_trades = 0

    total_profit = 0


    for trade in trade_history:

        if "profit" in trade:

            total_profit += trade["profit"]

            if trade["profit"] > 0:

                profitable_trades += 1


    win_rate = 0


    if total_trades > 0:

        win_rate = round(
            (profitable_trades / total_trades) * 100,
            2
        )


    return {

        "total_trades": total_trades,

        "total_profit": round(total_profit, 2),

        "win_rate": win_rate

    }
@app.get("/equity-curve")
def equity_curve():

    equity = [10000]

    current_balance = 10000


    for trade in trade_history:

        if "profit" in trade:

            current_balance += trade["profit"]

            equity.append(round(current_balance, 2))


    return {

        "equity": equity

    }
TELEGRAM_BOT_TOKEN = "8801428951:AAHXi6_o5HziMwLIC66yaUHOQ3Sdw5gRws8"

def send_telegram_message(message, chat_id):

    url = f"https://api.telegram.org/bot8801428951:AAHXi6_o5HziMwLIC66yaUHOQ3Sdw5gRws8/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message
    }

    requests.post(url, data=data)


def get_market_data():

    btc = yf.download(
        "BTC-USD",
        period="2d",
        interval="5m",
        progress=False
    )

    if btc.empty:
        return "N/A", "N/A", "ERROR"

    close_prices = btc["Close"]

    current_price = round(float(close_prices.iloc[-1]), 2)

    rsi = RSIIndicator(close_prices, window=14)

    latest_rsi = round(float(rsi.rsi().iloc[-1]), 2)

    if latest_rsi < 30:
        action = "BUY 🟢"

    elif latest_rsi > 70:
        action = "SELL 🔴"

    else:
        action = "HOLD 🟡"

    return current_price, latest_rsi, action


@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):

    print("Webhook hit")

    data = await request.json()

    message = data.get("message")

    if message:

        text = message.get("text", "")
        chat_id = message["chat"]["id"]

        if text == "/status":

            current_price, latest_rsi, action = get_market_data()

            response = f"""
📊 AIQuant Lite Status

💰 BTC Price: ${current_price}

📈 RSI: {latest_rsi}

🤖 Signal: {action}

✅ Bot Online
"""

        else:

            response = f"You said: {text}"

        send_telegram_message(response, chat_id)

    return {"ok": True}