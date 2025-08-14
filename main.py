from telethon import TelegramClient
from flask import Flask
import schedule
import time
import threading
from datetime import datetime, timedelta

# ==== CONFIGURATION ====
API_ID = 22339836     # Replace with your API ID
API_HASH = '0531739986bb128f3a8a9d39a2bd6c11'  # Replace with your API Hash
PHONE_NUMBER = '+6282294932904'  # Your phone number linked to Telegram

MESSAGE_TEXT = "Hello! This is an automated scheduled post."  # Message to send
START_TIME = "10:00"  # Start posting time (24-hour format)
END_TIME = "22:00"    # End posting time
INTERVAL_MINUTES = 60  # Interval between messages in minutes
# =======================

# Flask server for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Telegram client
client = TelegramClient('session', API_ID, API_HASH)

async def send_message_to_all_groups():
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, MESSAGE_TEXT)
                print(f"Sent to: {dialog.name}")
            except Exception as e:
                print(f"Error sending to {dialog.name}: {e}")

def job():
    now = datetime.now().strftime("%H:%M")
    if START_TIME <= now <= END_TIME:
        print(f"Posting at {now}")
        client.loop.create_task(send_message_to_all_groups())
    else:
        print(f"Outside schedule at {now}")

def scheduler():
    schedule.every(INTERVAL_MINUTES).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_bot():
    with client:
        client.loop.create_task(client.start(phone=PHONE_NUMBER))
        scheduler()

if __name__ == "__main__":
    # Run Flask in background
    threading.Thread(target=run_flask).start()

    # Start bot
    threading.Thread(target=start_bot).start()
