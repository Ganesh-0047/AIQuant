from fastapi import FastAPI, Request
import requests
import yfinance as yf
from ta.momentum import RSIIndicator

app = FastAPI()


TELEGRAM_BOT_TOKEN = "8801428951:AAFCZJGTvLKal0mvql3pW_Rzs1w6knYthLc"


def send_telegram_message(message, chat_id):

    url = f"https://api.telegram.org/bot8801428951:AAFCZJGTvLKal0mvql3pW_Rzs1w6knYthLc/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=data)


def get_market_data():

    print("Downloading BTC data...")

    try:

        btc = yf.download(
            "BTC-USD",
            period="2d",
            interval="5m",
            progress=False
        )

        print("BTC Data:")
        print(btc.head())

        if btc.empty:
            return "N/A", "N/A", "DATA ERROR"

        close_prices = btc["Close"]
        
        if hasattr(close_prices, "columns"):
            close_prices = close_prices.iloc[:, 0]
            print("TYPE:", type)
            print("LAST VALUE TYPE:", type(close_prices.iloc[-1]))
            print("LAST VALUE:", close_prices.iloc[-1])

        current_price = round(float(close_prices.iloc[-1].item()),2)

        rsi = RSIIndicator(
            close_prices,
            window=14
        )

        latest_rsi = round(float(rsi.rsi().iloc[-1].item()), 2)

        if latest_rsi < 30:
            action = "BUY 🟢"
        elif latest_rsi > 70:
            action = "SELL 🔴"
        else:
            action = "HOLD 🟡"

        return current_price, latest_rsi, action

    except Exception as e:

        print("MARKET DATA ERROR:", e)

        return "N/A", "N/A", "ERROR"



@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    
    print("Webhook hit")

    data = await request.json()

    message = data.get("message")

    if message:

        text = message.get("text", "")

        chat_id = message["chat"]["id"]


        if text == "/status":
            
            print("Status command received")

            current_price, latest_rsi, action = get_market_data()
            
            print("Price =", current_price)
            print("RSI =", latest_rsi)
            print("Action =", action)

            response = f"""
📊 AIQuant Lite Status

💰 BTC Price: ${current_price}

📈 RSI: {latest_rsi}

🤖 Signal: {action}

✅ Bot Online
"""

        else:

            response = f"You said: {text}"


        send_telegram_message(
            response,
            chat_id
        )


    return {"ok": True}
