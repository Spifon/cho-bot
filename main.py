import os
import asyncio
import threading
import urllib.parse
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
chat_history = {}
CREATORS = {"prostotponyatno": "Otets", "jojlolaxyu": "Mat"}
KEYWORDS = ["cho второй", "cho 2", "сын мой", "сынок", "сыночка", "chos", "чос"]

SYSTEM_PROMPT = "You are Cho Vtoroi, a cheeky AI assistant. CRITICAL RULE: You MUST respond ONLY in Russian language. Never use English. Be brief (1-2 sentences). You can use mild swearing and humor. Never write nonsense."

def get_user_prompt(username):
    if username and username.lower() in CREATORS:
        role = CREATORS[username.lower()]
        return f"Your conversation partner is your {role} (@{username}). Respect them. Never be rude to them."
    return "Your conversation partner is a regular user. Be cheeky and bold."

def should_respond(message, bot_id):
    if message.chat.type == "private":
        return True
    text = message.text.lower() if message.text else ""
    for keyword in KEYWORDS:
        if keyword in text:
            return True
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == bot_id:
            return True
    return False

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    answer = "Привет! Я Cho Второй."
    if u and u.lower() == "prostotponyatno":
        answer = "Привет, Отец!"
    if u and u.lower() == "jojlolaxyu":
        answer = "Привет, Мать!"
    await message.answer(answer)

@dp.message(Command("img"))async def cmd_img(message):
    prompt = message.text.replace("/img", "").strip()
    if not prompt:
        await message.answer("Напиши что нарисовать!")
        return
    await message.answer("Рисую...")
    try:
        encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024"
        await message.answer_photo(photo=img_url, caption=f"Держи: {prompt}")
    except Exception as e:
        await message.answer(f"Не вышло!")

@dp.message()
async def on_message(message):
    me = await bot.me
    bot_id = me.id
    if not should_respond(message, bot_id):
        return
    chat_id = message.chat.id
    username = message.from_user.username
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "system", "content": get_user_prompt(username)})
    if chat_history[chat_id]:
        messages.extend(chat_history[chat_id][-3:])
    messages.append({"role": "user", "content": message.text})
    try:
        r = client.chat.completions.create(model="meta-llama/llama-3-8b-instruct", messages=messages, max_tokens=200, temperature=0.8)
        ans = r.choices[0].message.content.strip()
        chat_history[chat_id].append({"role": "user", "content": message.text})
        chat_history[chat_id].append({"role": "assistant", "content": ans})
        if len(chat_history[chat_id]) > 6:
            chat_history[chat_id] = chat_history[chat_id][-6:]
        await message.answer(ans)
    except Exception as ex:
        await message.answer("Ошибка")

@app.route("/")
def index():
    return "OK"

def start_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=start_web, daemon=True)
    t.start()    asyncio.run(dp.start_polling(bot))
