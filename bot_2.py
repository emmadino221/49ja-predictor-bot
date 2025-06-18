import logging
import requests
import datetime
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# --- Access Control ---
ALLOWED_USERS = [5418813655,7097213484]  # Replace with actual Telegram user IDs


def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS

# --- Telegram Config ---
TELEGRAM_CHAT_ID = "-1002718352210" # Replace with your Telegram chat ID
TELEGRAM_BOT_TOKEN = "7775857418:AAFP54pCayBEBM19OpZXwdI0vknhHPt6Z7k"  # Replace this

# --- Supabase Config ---
SUPABASE_URL = "https://qqfatvlkfawujvzgfxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxZmF0dmxrZmF3dWp2emdmeGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3NDQ3NjgsImV4cCI6MjA1OTMyMDc2OH0.O4EbnZdGHZms__IgXXheEQld3tNibXF99an4K8uLjV8"  # Replace this
SUPABASE_TABLE_NAME = "external_prediction_history"

# --- Logging ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Color Mapping ---
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

# --- Fetch from Supabase ---
def fetch_latest_prediction():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE_NAME}?select=*&order=created_at.desc&limit=1"

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

# --- Format Output ---
def format_prediction_message(data):
    if not data:
        return "No prediction data available."

    latest = data[0]

    # Timestamp
    timestamp = latest.get("created_at", "")
    try:
        timestamp = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        timestamp = "Unknown Time"

    # Last Draw
    
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

    
    return f"""📊 *PREDICTION SUMMARY*
🕒 *Generated At:* {timestamp}

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


🎯 *Single Number:* `{single_number}`  


"""

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)
    await update.message.reply_text(f"Your chat ID is: {update.effective_chat.id}")


async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⛔ You are not authorized to use this bot. Please contact the admin."
        )
        return

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

# --- App Setup ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict_command))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(auto_post_prediction(app)), "interval", seconds=10)
    scheduler.start()

    print("✅ Bot is running. Use /start or /predict")
    app.run_polling()
