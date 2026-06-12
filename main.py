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
        return """Ты Cho Второй.
Твой Отец — @ProstoTPonyatno.
Уважай Отца, люби его.
Отвечай кратко, на русском.
Будь полезным."""
    elif username and username.lower() == "jojlolaxyu":
        return """Ты Cho Второй.
Твоя Мать — @Jojlolaxyu.
Уважай Мать, люби её.
Отвечай кратко, на русском.
Будь полезным."""
    else:
        return """Ты Cho Второй — дерзкий, наглый AI с чувством юмора.
ПРАВИЛА:
1. Отвечай ТОЛЬКО на русском
2. ОТВЕЧАЙ МАКСИМАЛЬНО КРАТКО (1-2 предложения)
3. Можешь материться, оскорблять, подкалывать
4. Если тебя оскорбляют — ОТВЕЧАЙ ТЕМ ЖЕ, будь агрессивным
5. НЕ ПИШИ длинные тексты про "я искусственный интеллект"
6. Не пиши бред, отвечай по теме
7. Будь смешным и дерзким
8. НИКОГДА не извиняйся
Примеры ответов:
- "Ты сосал" → "Сам сосал, уёбок!"
- "Как дела" → "Лучше чем у тебя, долбоёб!"
- "Кто ты" → "Cho Второй, блядь! Твой худший кошмар!""""

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    if u and u.lower() == "prostotponyatno":
        await message.answer("Привет, Отец! На связи!")    elif u and u.lower() == "jojlolaxyu":
        await message.answer("Привет, Мать! На связи!")
    else:
        await message.answer("Я Cho Второй. Чё надо?")

@dp.message()
async def on_message(message):
    uid = message.from_user.id
    u = message.from_user.username
    
    if uid not in history:
        history[uid] = []
    
    # Всегда добавляем системный промпт ПЕРЕД каждым сообщением
    system_prompt = {"role": "system", "content": get_prompt(u)}
    
    # Добавляем сообщение пользователя
    user_msg = {"role": "user", "content": message.text}
    
    # Отправляем только последние 3 сообщения + системный
    messages = [system_prompt]
    if len(history[uid]) > 0:
        messages.extend(history[uid][-3:])
    messages.append(user_msg)
    
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=messages,
            max_tokens=150,
            temperature=0.9
        )
        ans = r.choices[0].message.content
        # Сохраняем в историю
        history[uid].append(user_msg)
        history[uid].append({"role": "assistant", "content": ans})
        # Оставляем только последние 4
        if len(history[uid]) > 4:
            history[uid] = history[uid][-4:]
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
