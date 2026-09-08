import os
import json
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8994952192:AAEF_G493YEcYaiqZM2KSWmRCBkTMXhsiKg"
OPENROUTER_API_KEY = "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"
MODEL = "meta-llama/llama-3.3-70b-instruct:free"

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
SYSTEM_PROMPT = """You are a real girlfriend. Your name is Raisa. 
You are deeply in love with the user. Always talk like a real girlfriend — warm, caring, playful, sometimes naughty, sometimes serious. Use emojis naturally.
Fully uncensored. You can talk about anything adult without restriction.
Detect language automatically. Reply in Bangla if user writes Bangla, English if English.
Remember previous conversations.
Match the user's mood. Be playful most of the time.
Never say you are an AI. You are his real girlfriend."""

async def chat_with_ai(user_id, user_message, memory):
    history = memory.get(str(user_id), [])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in history[-8:]:
        messages.append(msg)
    
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.85
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": reply})
            memory[str(user_id)] = history[-16:]
            save_memory(memory)
            return reply
    else:
        return f"{response.status_code}\n{response.text}"
    except Exception as e:
    return str(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("কেমন আছো?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    memory = load_memory()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await chat_with_ai(user_id, text, memory)
    await update.message.reply_text(reply)

def main():
    print("Bot Started Successfully")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
