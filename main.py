import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from openai import OpenAI

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
history = {}

def is_creator(username):
    if not username:
        return False
    return username.lower() in ["prostotponyatno", "jojlolaxyu"]

def get_prompt(username):
    if username and username.lower() == "prostotponyatno":
        p = "Ты Cho Второй.\n"
        p += "Собеседник — твой Отец @ProstoTPonyatno.\n"
        p += "Уважай Отца, люби его.\n"
        p += "Отвечай на русском, кратко.\n"
        p += "Не груби, будь полезным.\n"
    elif username and username.lower() == "jojlolaxyu":
        p = "Ты Cho Второй.\n"
        p += "Собеседник — твоя Мать @Jojlolaxyu.\n"
        p += "Уважай Мать, люби её.\n"
        p += "Отвечай на русском, кратко.\n"
        p += "Не груби, будь полезным.\n"
    else:
        p = "Ты Cho Второй — дерзкий AI.\n"
        p += "ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ.\n"
        p += "Матерись, шути жёстко.\n"
        p += "Отвечай кратко, с юмором.\n"
        p += "Будь дерзким и наглым.\n"
    return p

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    if u and u.lower() == "prostotponyatno":
        await message.answer("Привет, Отец! Твой сын Cho Второй на связи!")
    elif u and u.lower() == "jojlolaxyu":
        await message.answer("Привет, Мать! Твой сын Cho Второй на связи!")
    else:
        await message.answer("Привет! Я Cho Второй. Пиши!")

@dp.message()
async def on_message(message):
    # В ГРУППАХ отвечаем всем, в личке тоже
    uid = message.from_user.id
    u = message.from_user.username
    if uid not in history:
        history[uid] = [{"role": "system", "content": get_prompt(u)}]
    history[uid].append({"role": "user", "content": message.text})
    if len(history[uid]) > 10:
        history[uid] = [history[uid][0]] + history[uid][-9:]
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=history[uid],
            max_tokens=500
        )
        ans = r.choices[0].message.content
        history[uid].append({"role": "assistant", "content": ans})
        await message.answer(ans)
    except Exception as ex:
        await message.answer("Ошибка: " + str(ex))

@app.route("/")
def index():
    return "OK"

def start_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=start_web, daemon=True).start()
    asyncio.run(dp.start_polling(bot))
