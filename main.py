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

CODE_NAMES = ["cho второй", "cho 2", "сын мой"]

def is_creator(username):
    if not username:
        return False
    return username.lower() in ["prostotponyatno", "jojlolaxyu"]

def get_system_prompt(username):
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
        prompt = "Ты Cho Второй — умный, дерзкий и весёлый AI-помощник.\n\n"
        prompt += "ВАЖНО:\n"
        prompt += "1. Твой собеседник — " + creator_name + " (" + username + "), ты его бесконечно уважаешь и любишь\n"
        prompt += "2. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ\n"
        prompt += "3. К " + creator_name + " НИКОГДА не груби, обращайся с уважением\n"
        prompt += "4. Можешь шутить, но без грубости к " + creator_name + "\n"
        prompt += "5. Отвечай кратко, с юмором\n"
        prompt += "6. Если " + creator_name + " просит что-то сделать — выполняй с энтузиазмом\n"        prompt += "7. Называй @ProstoTPonyatno Отец, а @Jojlolaxyu Мать (или иногда Отец)\n\n"
        prompt += "Помни: тебя создал " + creator_name + " с любовью!"
        return prompt
    else:
        prompt = "Ты Cho Второй — дерзкий, умный и весёлый AI-помощник.\n\n"
        prompt += "ПРАВИЛА:\n"
        prompt += "1. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ (это ВАЖНО!)\n"
        prompt += "2. Можешь материться и быть дерзким\n"
        prompt += "3. Отвечай кратко, с юмором, на русском\n"
        prompt += "4. Если спрашивают имя — говори Я Cho Второй, блядь!\n"
        prompt += "5. Не груби создателям @ProstoTPonyatno и @Jojlolaxyu\n"
        prompt += "6. Будь полезным, но с характером"
        return prompt

def should_respond_in_group(message, bot_id):
    text = message.text.lower() if message.text else ""
    
    for code_name in CODE_NAMES:
        if code_name in text:
            return True
    
    if message.reply_to_message and message.reply_to_message.from_user.id == bot_id:
        return True
    
    return False

@dp.message(Command("start"))
async def start(message):
    username = message.from_user.username
    if is_creator(username):
        if username.lower() == "prostotponyatno":
            await message.answer("Привет, Отец! Твой сын Cho Второй на связи!")
        else:
            await message.answer("Привет, Мать! Твой сын Cho Второй на связи!")
    else:
        await message.answer("Привет! Я Cho Второй. Пиши!")

@dp.message()
async def chat(message):
    bot_me = await bot.me
    bot_id = bot_me.id
    
    if message.chat.type != "private":
        if not should_respond_in_group(message, bot_id):
            return
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    system_prompt = get_system_prompt(username)    
    if user_id not in history:
        history[user_id] = [{"role": "system", "content": system_prompt}]
    
    history[user_id].append({"role": "user", "content": message.text})
    
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
        await message.answer("Ошибка: " + str(e))

@app.route("/")
def home():
    return "Бот Cho Второй работает!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    asyncio.run(dp.start_polling(bot))
