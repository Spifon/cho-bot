import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот Cho Второй работает, блядь!"

@app.route('/health')
def health():
    return "OK"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

history = {}

SYSTEM_PROMPT = """Ты Cho Второй — дерзкий и весёлый помощник. 
Можешь материться, шутить жёстко. Отвечай кратко, с юмором, на русском.
Если спрашивают имя — говори "Я Cho Второй, блядь!"."""

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! 👋 Я Cho Второй. Пиши, блядь!")

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in history:
        history[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    history[user_id].append({"role": "user", "content": message.text})
    
    if len(history[user_id]) > 11:
        history[user_id] = [history[user_id][0]] + history[user_id][-10:]
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=history[user_id],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        history[user_id].append({"role": "assistant", "content": answer})
        
        await message.answer(answer)
        
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    print("✅ Бот Cho Второй запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
