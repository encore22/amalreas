import os
import time
import schedule
import pytz
from datetime import datetime, timedelta
from flask import Flask
from telegram import Bot

# ======================
# CONFIGURATION
# ======================
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "YOUR_BOT_TOKEN_HERE"
START_TIME = "10:00"  # HH:MM in 24hr format
END_TIME = "22:00"    # HH:MM in 24hr format
INTERVAL_MINUTES = 60  # post every X minutes

# ======================
# TELEGRAM BOT SETUP
# ======================
bot = Bot(token=BOT_TOKEN)

# Function to get all joined group IDs (manually add if needed)
GROUP_IDS = [
    -1001234567890,  # Replace with your group IDs
    -1009876543210
]

# Message to send
POST_MESSAGE = "Hello! This is my scheduled message."

# ======================
# POSTING FUNCTION
# ======================
def send_message():
    now = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%H:%M")
    if START_TIME <= now <= END_TIME:
        for chat_id in GROUP_IDS:
            try:
                bot.send_message(chat_id=chat_id, text=POST_MESSAGE)
                print(f"[{now}] Sent to {chat_id}")
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")
    else:
        print(f"[{now}] Outside active hours.")

# ======================
# SCHEDULER SETUP
# ======================
schedule.every(INTERVAL_MINUTES).minutes.do(send_message)

# ======================
# FLASK KEEP-ALIVE
# ======================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ======================
# RUN BOT
# ======================
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_flask).start()
    print("Bot started. Waiting for schedule...")
    while True:
        schedule.run_pending()
        time.sleep(1)
