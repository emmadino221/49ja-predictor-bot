import logging
import requests
import datetime
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your chat ID is: {update.effective_chat.id}")


# Set your Telegram chat ID where the bot will post predictions
 # Replace with your actual chat ID
TELEGRAM_CHAT_ID = "@mydrawpredictor_bot"


# Set your credentials
SUPABASE_URL = "https://qqfatvlkfawujvzgfxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxZmF0dmxrZmF3dWp2emdmeGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3NDQ3NjgsImV4cCI6MjA1OTMyMDc2OH0.O4EbnZdGHZms__IgXXheEQld3tNibXF99an4K8uLjV8"
SUPABASE_TABLE_NAME = "external_prediction_history"
TELEGRAM_BOT_TOKEN = "7775857418:AAFP54pCayBEBM19OpZXwdI0vknhHPt6Z7k"

# Logging config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def get_color_by_number(number):
    if number == 49:
        return "yellow"
    if (number - 1) % 3 == 0:
        return "red"
    elif (number - 2) % 3 == 0:
        return "blue"
    else:
        return "green"

def get_color_emoji(color):
    return {
        "red": "🔴",
        "blue": "🔵",
        "green": "🟢",
        "yellow": "🟡"
    }.get(color.lower(), "")

def fetch_latest_prediction():
    url = f"{SUPABASE_URL}/prediction_data?select=*&order=created_at.desc&limit=1"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Failed to fetch prediction data: %s", response.text)
        return {}
    return response.json()

def format_prediction_message(data):
    if not data:
        return "No prediction data available."

    latest = data[0]

    # Format timestamp
    timestamp = latest.get("created_at", "")
    try:
        timestamp = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        timestamp = "Unknown Time"

    # Draw results and total
    last_draw = latest.get("last_draw_results", {})
    total = last_draw.get("total", "N/A")
    last_numbers = last_draw.get("numbers", [])
    numbers_with_colors = [(num, get_color_by_number(num)) for num in last_numbers]
    draw_text = ", ".join([f"{num} ({get_color_emoji(color)})" for num, color in numbers_with_colors])

    # Prediction outputs
    high_low_mid = latest.get("high_low_mid_prediction", "N/A")
    rainbow = latest.get("rainbow_prediction", "N/A")
    total_color = latest.get("total_color_prediction", "N/A")
    bet_zero = latest.get("bet_zero_prediction", "N/A")
    bet49 = latest.get("bet49_prediction", "N/A")

    message = f"""📊 *PREDICTION SUMMARY*
🕒 *Generated At:* {timestamp}

🎲 *Last Draw Result:*  
{draw_text}  
🔢 *Total:* {total}

🎯 *Predictions:*  
- High/Low/Mid: `{high_low_mid}`  
- Rainbow: `{rainbow}`  
- Total Color: `{total_color}`  
- Bet Zero (unlikely numbers): `{bet_zero}`  
- Bet49 (likely numbers): `{bet49}`  
"""

    return message

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = fetch_latest_prediction()
    message = format_prediction_message(data)
    await update.message.reply_text(message, parse_mode="Markdown")

async def auto_post_prediction(application):
    try:
        data = fetch_latest_prediction()
        message = format_prediction_message(data)
        await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        logger.error("Auto post failed: %s", e)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Manual prediction command
    app.add_handler(CommandHandler("predict", predict_command))

    # Scheduler for auto-posting every 20 seconds
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(auto_post_prediction(app)), "interval", seconds=20)
    scheduler.start()

    print("✅ Bot is running. Use /predict in Telegram or wait for scheduled posts every 20 seconds.")
    app.run_polling()
