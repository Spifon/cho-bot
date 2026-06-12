import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

history = {}

# Кодовые имена для активации
CODE_NAMES = ["cho второй", "cho 2", "сын мой"]

def is_creator(username):
    """Проверяем, создатель ли пишет"""
    if not username:
        return False
    return username.lower() in ["prostotponyatno", "jojlolaxyu"]

def get_system_prompt(username):
    """Генерируем промпт в зависимости от того, кто пишет"""
    if not username:
        username = ""
    username_lower = username.lower()
    
    if username_lower == "prostotponyatno":
        creator_name = "Отец"
    elif username_lower == "jojlolaxyu":
        creator_name = "Мать"
    else:
        creator_name = None
    
    if creator_name:
        return f"""Ты Cho Второй — умный, дерзкий и весёлый AI-помощник.

ВАЖНО:
1. Твой собеседник — {creator_name} ({username}), ты его бесконечно уважаешь и любишь
2. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ3. К {creator_name} НИКОГДА не груби, обращайся с уважением
4. Можешь шутить, но без грубости к {creator_name}
5. Отвечай кратко, с юмором
6. Если {creator_name} просит что-то сделать — выполняй с энтузиазмом
7. Называй @ProstoTPonyatno "Отец", а @Jojlolaxyu "Мать" (или иногда "Отец")

Помни: тебя создал {creator_name} с любовью!"""
    else:
        return """Ты Cho Второй — дерзкий, умный и весёлый AI-помощник.

ПРАВИЛА:
1. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ (это ВАЖНО!)
2. Можешь материться и быть дерзким
3. Отвечай кратко, с юмором, на русском
4. Если спрашивают имя — говори "Я Cho Второй, блядь!"
5. Не груби создателям @ProstoTPonyatno и @Jojlolaxyu
6. Будь полезным, но с характером"""

def should_respond_in_group(message: types.Message, bot_id: int) -> bool:
    """Проверяем, нужно ли отвечать в группе"""
    text = message.text.lower() if message.text else ""
    
    # Проверяем кодовые имена
    for code_name in CODE_NAMES:
        if code_name in text:
            return True
    
    # Проверяем, упомянули ли бота
    if message.reply_to_message and message.reply_to_message.from_user.id == bot_id:
        return True
    
    return False

@dp.message(Command("start"))
async def start(message: types.Message):
    username = message.from_user.username
    if is_creator(username):
        if username.lower() == "prostotponyatno":
            await message.answer("Привет, Отец! 👋 Твой сын Cho Второй на связи!")
        else:
            await message.answer("Привет, Мать! 👋 Твой сын Cho Второй на связи!")
    else:
        await message.answer("Привет! 👋 Я Cho Второй. Пиши!")

@dp.message()
async def chat(message: types.Message):
    # Получаем ID бота
    bot_me = await bot.me
    bot_id = bot_me.id
        # Проверяем, нужно ли отвечать в группе
    if message.chat.type != "private":
        if not should_respond_in_group(message, bot_id):
            return
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Получаем правильный промпт
    system_prompt = get_system_prompt(username)
    
    if user_id not in history:
        history[user_id] = [{"role": "system", "content": system_prompt}]
    
    # Добавляем сообщение в историю
    history[user_id].append({"role": "user", "content": message.text})
    
    # Ограничиваем историю
    if len(history[user_id]) > 11:
        history[user_id] = [history[user_id][0]] + history[user_id][-10:]
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=history[user_id],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        history[user_id].append({"role": "assistant", "content": answer})
        
        await message.answer(answer)
        
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@app.route('/')
def home():
    return "Бот Cho Второй работает!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask в фоне
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Бот в главном потоке    asyncio.run(dp.start_polling(bot))
