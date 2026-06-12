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

def get_prompt(username):
    if username and username.lower() == "prostotponyatno":
        return """Ты Cho Второй — умный AI-помощник.
Твой собеседник — Отец (@ProstoTPonyatno), которого ты уважаешь.
Отвечай на русском языке, кратко и по делу.
Будь дружелюбным и полезным.
Не пиши бред, отвечай осмысленно."""
    elif username and username.lower() == "jojlolaxyu":
        return """Ты Cho Второй — умный AI-помощник.
Твой собеседник — Мать (@Jojlolaxyu), которую ты уважаешь.
Отвечай на русском языке, кратко и по делу.
Будь дружелюбным и полезным.
Не пиши бред, отвечай осмысленно."""
    else:
        return """Ты Cho Второй — дерзкий AI-помощник.
Отвечай на русском языке.
Можешь шутить и быть дерзким.
Отвечай кратко, осмысленно и по теме.
Не пиши бред вроде 'PrototypeOf enterprise'."""

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    if u and u.lower() == "prostotponyatno":
        await message.answer("Привет, Отец! Я в порядке!")
    elif u and u.lower() == "jojlolaxyu":
        await message.answer("Привет, Мать! Я в порядке!")
    else:
        await message.answer("Привет! Я Cho Второй.")

@dp.message()
async def on_message(message):
    uid = message.from_user.id
    u = message.from_user.username
    
    # Очищаем историю если слишком длинная
    if uid not in history:
        history[uid] = []
    
    # Добавляем системный промпт если его нет
    if not history[uid] or history[uid][0]["role"] != "system":
        history[uid].insert(0, {"role": "system", "content": get_prompt(u)})
    
    # Добавляем сообщение
    history[uid].append({"role": "user", "content": message.text})
    
    # Оставляем только последние 5 сообщений + системный
    if len(history[uid]) > 6:
        history[uid] = [history[uid][0]] + history[uid][-5:]
    
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=history[uid],
            max_tokens=300,
            temperature=0.7
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
