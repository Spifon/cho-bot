import os
import asyncio
import threading
import aiohttp
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

CREATORS = {
    "prostotponyatno": "Otets",
    "jojlolaxyu": "Mat"
}

KEYWORDS = ["cho второй", "cho 2", "сын мой", "сынок", "сыночка", "chos", "чос", "chosecond"]

def get_system_prompt():
    return "Ty Cho Vtoroi - derzki AI-pomoshchnik. Otvechai TOLKO na russkom. Bud kratkim (1-2 predlozhenija). Mozhesh materitsja i shutit. Ne pishi bred."

def get_user_prompt(username):
    if username and username.lower() in CREATORS:
        role = CREATORS[username.lower()]
        return f"SOBESEDIK - tvoj {role} (@{username}). Uvazhai ego. Ne grubi."
    else:
        return "SOBESEDIK - obychnyj polzovatel. Otvechai derzko."

def should_respond(message, bot_id):
    """Проверяем нужно ли отвечать в группе"""
    # В личке отвечаем всегда
    if message.chat.type == "private":
        return True
    
    text = message.text.lower() if message.text else ""
    
    # Проверяем ключевые слова
    for keyword in KEYWORDS:
        if keyword in text:
            return True
    
    # Если упомянули бота
    if bot.mentioned(message):        return True
    
    # Если ответ на сообщение бота
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == bot_id:
            return True
    
    return False

async def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
    return url

async def generate_music(prompt):
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.musicgen.com/generate"
            data = {"prompt": prompt, "duration": 10}
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("audio_url")
    except:
        return None
    return None

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    if u and u.lower() == "prostotponyatno":
        await message.answer("Привет, Отец!")
    elif u and u.lower() == "jojlolaxyu":
        await message.answer("Привет, Мать!")
    else:
        await message.answer("Привет! Я Cho Второй.")

@dp.message(Command("img"))
async def cmd_img(message):
    prompt = message.text.replace("/img", "").strip()
    if not prompt:
        await message.answer("Напиши что нарисовать! Пример: /img кот в космосе")
        return
    
    await message.answer("Рисую...")
    
    try:
        img_url = await generate_image(prompt)
        await message.answer_photo(photo=img_url, caption=f"Держи, блядь! {prompt}")
    except Exception as e:
        await message.answer("Не вышло нарисовать, сука!")
@dp.message(Command("music"))
async def cmd_music(message):
    prompt = message.text.replace("/music", "").strip()
    if not prompt:
        await message.answer("Напиши какую музыку создать! Пример: /music веселая песенка")
        return
    
    await message.answer("Создаю музыку...")
    
    try:
        audio_url = await generate_music(prompt)
        if audio_url:
            await message.answer_audio(audio=audio_url, caption=f"Музыка: {prompt}")
        else:
            await message.answer("Не получилось создать музыку!")
    except Exception as e:
        await message.answer("Ошибка при создании музыки!")

@dp.message()
async def on_message(message):
    me = await bot.me
    bot_id = me.id
    
    # Проверяем нужно ли отвечать
    if not should_respond(message, bot_id):
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    
    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(username)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": user_prompt}
    ]
    
    if chat_history[chat_id]:
        messages.extend(chat_history[chat_id][-3:])
    
    messages.append({"role": "user", "content": message.text})
    
    try:
        r = client.chat.completions.create(            model="meta-llama/llama-3-8b-instruct",
            messages=messages,
            max_tokens=200,
            temperature=0.8
        )
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=start_web, daemon=True).start()
    asyncio.run(dp.start_polling(bot))
