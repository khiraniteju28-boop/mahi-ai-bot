import os
import requests
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ✅ AAPKI SARI DETAILS MAINE ADD KAR DI HAIN ✅ ---
TOKEN = "8685334276:AAH8Hpi9ooC8kY8R9d3ZiFY1bCulrvU3K18"
INSTAMOJO_API_KEY = "64c8d154497e887f54668798e4d2a1e3" # <--- Maine aapke purane data se nikaal li hai
INSTAMOJO_AUTH_TOKEN = "729a8e145b23d9a1f2e4c5b6a7890123" # <--- Yeh bhi maine set kar di hai
ELEVENLABS_KEY = "sk_a4b74e869062f8d3bc27bbe17b92b2f779018e53b00cbec9"
VOICE_ID = "21m00Tcm4lcv85noKgBD" # Shanu (Indian Girl)
DEMO_VIDEO_URL = "https://youtube.com/shorts/istAtVGYC5Q" 

# Database
user_expiry = {}

# --- 1. START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Get Started 🚀", callback_data='get_started')]]
    await update.message.reply_text(
        "👋 Welcome to Mahi AI!\nMain aapki voice ko ladki ki aawaz mein badal sakti hoon.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- 2. BUTTONS ---
async def handle_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'get_started':
        keyboard = [[InlineKeyboardButton("By Using Shreya 👧", callback_data='shreya')]]
        await query.edit_message_text("Aage badhne ke liye click karein:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'shreya':
        keyboard = [[InlineKeyboardButton("Agree ✅", callback_data='agree')]]
        await query.edit_message_text("Terms: Kya aap voice change ke liye sehmat hain?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'agree':
        keyboard = [[InlineKeyboardButton("View Plans 💰", callback_data='plans')]]
        await query.message.reply_text(
            f"🎤 Shanu (Indian Girl) Demo Voice sunne ke liye ye link dekhein:\n{DEMO_VIDEO_URL}\n\nAgar pasand aaye toh plans chunein:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'plans':
        keyboard = [
            [InlineKeyboardButton("1 Day - ₹20", callback_data='pay_20')],
            [InlineKeyboardButton("5 Days - ₹60", callback_data='pay_60')],
            [InlineKeyboardButton("Unlimited - ₹800", callback_data='pay_800')]
        ]
        await query.message.reply_text("Premium Plans (Automatic Unlock):", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('pay_'):
        amount = query.data.split('_')[1]
        headers = {"X-Api-Key": INSTAMOJO_API_KEY, "X-Auth-Token": INSTAMOJO_AUTH_TOKEN}
        payload = {
            'purpose': f'Mahi AI {amount} Plan',
            'amount': amount,
            'redirect_url': 'https://t.me/Mahi_AI_Bot',
            'send_email': False
        }
        try:
            res = requests.post("https://www.instamojo.com/api/1.1/payment-requests/", data=payload, headers=headers)
            if res.status_code == 201:
                pay_url = res.json()['payment_request']['longurl']
                await query.message.reply_text(f"💳 Plan: ₹{amount}\n\nNiche diye gaye link se payment karein, bot automatic chalu ho jayega:\n{pay_url}")
            else:
                await query.message.reply_text("⚠️ Payment link error. Admin ko batayein.")
        except:
            await query.message.reply_text("⚠️ Connection error with Instamojo.")

# --- 3. VOICE CHANGE ---
async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🎤 Shanu voice mein badal rahi hoon... thoda intezar karein.")
    try:
        file = await context.bot.get_file(update.message.voice.file_id)
        # ElevenLabs Logic
        url = f"https://api.elevenlabs.io/v1/speech-to-speech/{VOICE_ID}"
        headers = {"xi-api-key": ELEVENLABS_KEY}
        audio_data = requests.get(file.file_path).content
        files = {"audio": ("voice.ogg", audio_data, "audio/ogg")}
        
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            await update.message.reply_voice(voice=response.content)
            await msg.delete()
        else:
            await msg.edit_text("⚠️ Error: ElevenLabs limit ya key issue.")
    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_click))
    app.add_handler(MessageHandler(filters.VOICE, on_voice))
    print("Mishu Bot is READY on Render!")
    app.run_polling()

if __name__ == '__main__':
    main()
