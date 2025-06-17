import os
import requests
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_color_by_number(number):
    if number == 49:
        return "yellow"
    if (number - 1) % 3 == 0:
        return "red"
    elif (number - 2) % 3 == 0:
        return "blue"
    else:
        return "green"


# Set your tokens
SUPABASE_URL = "https://qqfatvlkfawujvzgfxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxZmF0dmxrZmF3dWp2emdmeGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3NDQ3NjgsImV4cCI6MjA1OTMyMDc2OH0.O4EbnZdGHZms__IgXXheEQld3tNibXF99an4K8uLjV8"
SUPABASE_TABLE_NAME = "external_prediction_history"
TELEGRAM_BOT_TOKEN = "7775857418:AAFP54pCayBEBM19OpZXwdI0vknhHPt6Z7k"

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper to fetch prediction
def fetch_latest_prediction():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE_NAME}?order=created_at.desc&limit=1"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    logger.debug("Supabase response: %s", data)

    if not data:
        raise ValueError("No prediction data available.")
    return data

# Color to emoji mapping
def get_color_emoji(color):
    color_map = {
        "red": "🔴",
        "green": "🟢",
        "blue": "🔵",
        "yellow": "🟡"
    }
    return color_map.get(color.lower(), color)

# Format message
def format_prediction_message(data):
    latest = data[0]

    betzero = latest.get("betzero", "N/A")
    color2plus = latest.get("color2plus", "N/A")
    color3plus = latest.get("color3plus", "N/A")
    high_low = latest.get("high_low", "N/A")
    single_number = latest.get("single_number", "N/A")

    betzero_streak = latest.get("betzero_streak", "N/A")
    color2plus_streak = latest.get("color2plus_streak", "N/A")
    color3plus_streak = latest.get("color3plus_streak", "N/A")
    high_low_streak = latest.get("high_low_streak", "N/A")
    single_number_streak = latest.get("single_number_streak", "N/A")

    

    # ... other variables unchanged ...

    last_draw = latest.get("last_draw_results", {})
    total = last_draw.get("total", "N/A")

    # Assuming 'numbers' key holds the list of last drawn numbers:
    last_numbers = last_draw.get("numbers", [])
    numbers_with_colors = [(num, get_color_by_number(num)) for num in last_numbers]

    draw_text = ", ".join([f"{num} ({get_color_emoji(color)})" for num, color in numbers_with_colors])

    
    message = f"""📊 *PREDICTION SUMMARY*

🎲 *Last Draw Result:*  
{draw_text}  
🔢 *Total:* {total}

🎯 *BetZero:* `{betzero}`  
📈 Streak: {betzero_streak}

🟢 *Color 2+ Appearing:* `{color2plus}`  
📈 Streak: {color2plus_streak}

🔺 *High/Low:* `{high_low}`  
📈 Streak: {high_low_streak}


🔵 *Color 3+ Appearing:* `{color3plus or "N/A"}`  
📈 Streak: {color3plus_streak or "N/A"}

🎯 *Single Number:* `{single_number}`  
📈 Streak: {single_number_streak}







"""

    return message

# Telegram command
async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_latest_prediction()
        message = format_prediction_message(data)
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error("Error sending prediction: %s", e)
        await update.message.reply_text("⚠️ Failed to fetch prediction.")

# Main bot app
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("predict", predict_command))

    print("✅ Bot is running. Send /predict in Telegram.")
    app.run_polling()













