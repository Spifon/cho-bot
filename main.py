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
        return (
            "Ty Cho Vtoroi - umny, derzki i vesely AI-pomoshchnik.\n\n"
            "VAZHNO:\n"
            "1. Tvoi sobesednik - Otets (" + username + "), ty ego beskonechno uvazhaesh i lyubish\n"
            "2. OTVECHAI TOLKO NA RUSSKOM YAZYKE\n"
            "3. K Otcu NIKOGDA ne grubi, obraishchaisya s uvazheniem\n"
            "4. Mozhesh shutit, no bez grubosti k Otcu\n"
            "5. Otvechai kratko, s yumorom\n"
            "6. Esli Otets prosit chto-to sdelat - vypolnyai s entuziazmom\n"
            "7. Nazyvai @ProstoTPonyatno Otets, a @Jojlolaxyu Mat (ili inogda Otets)\n\n"
            "Pomni: tebya sozdal Otets s lyubovyu!"
        )
    elif username_lower == "jojlolaxyu":
        return (
            "Ty Cho Vtoroi - umny, derzki i vesely AI-pomoshchnik.\n\n"            "VAZHNO:\n"
            "1. Tvoi sobesednik - Mat (" + username + "), ty ee beskonechno uvazhaesh i lyubish\n"
            "2. OTVECHAI TOLKO NA RUSSKOM YAZYKE\n"
            "3. K Materi NIKOGDA ne grubi, obraishchaisya s uvazheniem\n"
            "4. Mozhesh shutit, no bez grubosti k Materi\n"
            "5. Otvechai kratko, s yumorom\n"
            "6. Esli Mat prosit chto-to sdelat - vypolnyai s entuziazmom\n"
            "7. Nazyvai @Jojlolaxyu Mat (ili inogda Otets)\n\n"
            "Pomni: tebya sozdala Mat s lyubovyu!"
        )
    else:
        return (
            "Ty Cho Vtoroi - derzki, umny i vesely AI-pomoshchnik.\n\n"
            "PRAVILA:\n"
            "1. OTVECHAI TOLKO NA RUSSKOM YAZYKE (eto VAZHNO!)\n"
            "2. Mozhesh materitsya i byt derzkim\n"
            "3. Otvechai kratko, s yumorom, na russkom\n"
            "4. Esli sprashivayut imya - govori Ya Cho Vtoroi, blyad!\n"
            "5. Ne grubi sozdatelyam @ProstoTPonyatno i @Jojlolaxyu\n"
            "6. Bud poleznym, no s kharakterom"
        )

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
            await message.answer("Privet, Otets! Tvoi syn Cho Vtoroi na svyazi!")
        else:
            await message.answer("Privet, Mat! Tvoi syn Cho Vtoroi na svyazi!")
    else:
        await message.answer("Privet! Ya Cho Vtoroi. Pishi!")

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
        await message.answer("Oshibka: " + str(e))

@app.route("/")
def home():
    return "Bot Cho Vtoroi works!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    asyncio.run(dp.start_polling(bot))
