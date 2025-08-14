import schedule
import time
from datetime import datetime
from pyrogram import Client, filters
from flask import Flask
from threading import Thread
from pyngrok import ngrok

# ==============================
# 🔹 CONFIGURATION (EDIT THESE ONCE)
# ==============================
API_ID = 1234567                # Your Telegram API ID
API_HASH = "your_api_hash"      # Your Telegram API Hash
SESSION_STRING = "your_session_string"  # Generated with Pyrogram
OWNER_ID = 123456789            # Your Telegram user ID (so only you can control)
PORT = 8080                     # Flask server port
# ==============================

# Default settings (can be changed from Telegram)
MESSAGE_TEXT = "Hello! This is my scheduled auto-post."
INTERVAL_MINUTES = 30
START_TIME = "09:00"
END_TIME = "18:00"
POSTING_ENABLED = True

# Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.start()
    public_url = ngrok.connect(PORT)
    print(f"🌐 Public Ngrok URL: {public_url}")

# Telegram client
app_telegram = Client(
    "my_account",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Send message to all groups
def send_to_all_groups():
    global MESSAGE_TEXT, START_TIME, END_TIME, POSTING_ENABLED
    now = datetime.now().strftime("%H:%M")
    if POSTING_ENABLED and START_TIME <= now <= END_TIME:
        with app_telegram:
            dialogs = app_telegram.get_dialogs()
            for dialog in dialogs:
                if dialog.chat.type in ["group", "supergroup"]:
                    try:
                        app_telegram.send_message(dialog.chat.id, MESSAGE_TEXT)
                        print(f"✅ Sent to {dialog.chat.title}")
                    except Exception as e:
                        print(f"❌ Failed in {dialog.chat.title}: {e}")
    else:
        print(f"⏳ Not in active time range ({START_TIME} - {END_TIME}) or posting disabled")

# Control commands
@app_telegram.on_message(filters.private & filters.user(OWNER_ID))
def control_panel(client, message):
    global MESSAGE_TEXT, START_TIME, END_TIME, INTERVAL_MINUTES, POSTING_ENABLED

    text = message.text.strip()

    if text.lower().startswith("/setmsg "):
        MESSAGE_TEXT = text[8:]
        message.reply_text(f"✅ Message updated to:\n{MESSAGE_TEXT}")

    elif text.lower().startswith("/setstart "):
        START_TIME = text[10:]
        message.reply_text(f"✅ Start time updated to {START_TIME}")

    elif text.lower().startswith("/setend "):
        END_TIME = text[8:]
        message.reply_text(f"✅ End time updated to {END_TIME}")

    elif text.lower().startswith("/setinterval "):
        try:
            INTERVAL_MINUTES = int(text[13:])
            schedule.clear()
            schedule.every(INTERVAL_MINUTES).minutes.do(send_to_all_groups)
            message.reply_text(f"✅ Interval updated to {INTERVAL_MINUTES} minutes")
        except:
            message.reply_text("❌ Invalid interval")

    elif text.lower() == "/startposting":
        POSTING_ENABLED = True
        message.reply_text("✅ Posting enabled")

    elif text.lower() == "/stopposting":
        POSTING_ENABLED = False
        message.reply_text("⏹ Posting disabled")

    elif text.lower() == "/status":
        message.reply_text(
            f"📊 **Bot Status**\n\n"
            f"Message: {MESSAGE_TEXT}\n"
            f"Start Time: {START_TIME}\n"
            f"End Time: {END_TIME}\n"
            f"Interval: {INTERVAL_MINUTES} minutes\n"
            f"Posting Enabled: {POSTING_ENABLED}"
        )

    else:
        message.reply_text(
            "📜 **Commands:**\n"
            "/setmsg <text> - Change post message\n"
            "/setstart <HH:MM> - Set start time\n"
            "/setend <HH:MM> - Set end time\n"
            "/setinterval <minutes> - Set interval\n"
            "/startposting - Enable posting\n"
            "/stopposting - Disable posting\n"
            "/status - Show settings"
        )

# Schedule jobs
def schedule_job():
    schedule.every(INTERVAL_MINUTES).minutes.do(send_to_all_groups)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    keep_alive()
    Thread(target=schedule_job).start()
    app_telegram.run()
