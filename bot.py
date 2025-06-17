





from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

BOT_TOKEN = "7775857418:AAFP54pCayBEBM19OpZXwdI0vknhHPt6Z7k"  # Replace this
SUPABASE_URL = "https://qqfatvlkfawujvzgfxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxZmF0dmxrZmF3dWp2emdmeGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3NDQ3NjgsImV4cCI6MjA1OTMyMDc2OH0.O4EbnZdGHZms__IgXXheEQld3tNibXF99an4K8uLjV8"
SUPABASE_TABLE = "external_prediction_history"  # Replace with your table name


def fetch_latest_prediction():
    url = "https://qqfatvlkfawujvzgfxku.supabase.co/rest/v1/external_prediction_history?select=*&order=created_at.desc&limit=1"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    try:
        data = response.json()
        print("DEBUG - Supabase response:", data)

        if isinstance(data, list) and data:
            latest = data[0]

            # Parse draw numbers and colors
            last_numbers = latest.get('last_draw_results', {}).get('numbers', [])
            last_colors = latest.get('last_draw_results', {}).get('numbersWithColors', [])
            draw_total = latest.get('last_draw_results', {}).get('total', 'N/A')

            colored_nums = []
            for pair in last_colors:
                num, color = pair
                emoji = {
                    "red": "🟥",
                    "blue": "🟦",
                    "green": "🟩",
                    "yellow": "🟨"
                }.get(color.lower(), "⚪️")
                colored_nums.append(f"{emoji}{num}")

            message = [
                f"🎯 *BetZero*: {latest.get('betzero', 'N/A')}",
                f"📈 Streak: {latest.get('betzero_streak', 'N/A')} (✅{latest.get('betzero_total_wins', 0)} ❌{latest.get('betzero_total_losses', 0)})",

                f"\n🌈 *Color 2+ Appearing*: {latest.get('color2plus', 'N/A')}",
                f"📈 Streak: {latest.get('color2plus_streak', 'N/A')} (✅{latest.get('color2plus_total_wins', 0)} ❌{latest.get('color2plus_total_losses', 0)})",

                f"\n🌈 *Color 3+ Appearing*: {latest.get('color3plus', 'N/A')}",
                f"📈 Streak: {latest.get('color3plus_streak', 'N/A')} (✅{latest.get('color3plus_total_wins', 0)} ❌{latest.get('color3plus_total_losses', 0)})",

                f"\n📊 *High/Low*: {latest.get('high_low', 'N/A')}",
                f"📈 Streak: {latest.get('high_low_streak', 'N/A')} (✅{latest.get('high_low_total_wins', 0)} ❌{latest.get('high_low_total_losses', 0)})",

                f"\n🔢 *Single Number*: {latest.get('single_number', 'N/A')}",
                f"📈 Streak: {latest.get('single_number_streak', 'N/A')} (✅{latest.get('single_number_total_wins', 0)} ❌{latest.get('single_number_total_losses', 0)})",

                f"\n🎲 *Last Draw*: {', '.join(map(str, last_numbers))}",
                f"🎨 Colors: {', '.join(colored_nums)}",
                f"🔢 Total: {draw_total}"
            ]

            return message
        else:
            return ["⚠️ No predictions found."]
    except Exception as e:
        print("Error decoding Supabase response:", e)
        return ["⚠️ Failed to retrieve predictions."]

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prediction = fetch_latest_prediction()
    await update.message.reply_text(f"Prediction: {prediction}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("predict", predict_command))
    print("✅ Bot is running. Send /predict in Telegram.")
    app.run_polling()

if __name__ == "__main__":
    main()
