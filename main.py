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
CODE_NAMES = ["cho vtoroi", "cho 2", "syn moi"]

def is_creator(username):
    if not username:
        return False
    users = ["prostotponyatno", "jojlolaxyu"]
    return username.lower() in users

def get_system_prompt(username):
    if not username:
        username = ""
    u = username.lower()
    
    if u == "prostotponyatno":
        p = "Ty Cho Vtoroi - umny i vesely AI.\n"
        p += "Sobesednik - Otets.\n"
        p += "Uvazhai Otca.\n"
        p += "Otvechai na russkom.\n"
        p += "Ne grubi Otcu.\n"
        p += "Bud veselym.\n"
        return p
    elif u == "jojlolaxyu":
        p = "Ty Cho Vtoroi - umny i vesely AI.\n"
        p += "Sobesednik - Mat.\n"
        p += "Uvazhai Mat.\n"
        p += "Otvechai na russkom.\n"
        p += "Ne grubi Materi.\n"
        p += "Bud veselym.\n"
        return p
    else:
        p = "Ty Cho Vtoroi - derzki AI.\n"
        p += "Otvechai na russkom.\n"        p += "Mozhesh materitsya.\n"
        p += "Bud kratkim.\n"
        return p

def should_respond(msg, bid):
    t = msg.text.lower() if msg.text else ""
    for name in CODE_NAMES:
        if name in t:
            return True
    if msg.reply_to_message:
        if msg.reply_to_message.from_user.id == bid:
            return True
    return False

@dp.message(Command("start"))
async def start_cmd(msg):
    u = msg.from_user.username
    if is_creator(u):
        if u and u.lower() == "prostotponyatno":
            await msg.answer("Privet Otets!")
        else:
            await msg.answer("Privet Mat!")
    else:
        await msg.answer("Privet! Ya Cho Vtoroi.")

@dp.message()
async def chat(msg):
    me = await bot.me
    bid = me.id
    
    if msg.chat.type != "private":
        if not should_respond(msg, bid):
            return
    
    uid = msg.from_user.id
    u = msg.from_user.username
    prompt = get_system_prompt(u)
    
    if uid not in history:
        history[uid] = []
        history[uid].append({"role": "system", "content": prompt})
    
    history[uid].append({"role": "user", "content": msg.text})
    
    if len(history[uid]) > 11:
        history[uid] = [history[uid][0]] + history[uid][-10:]
    
    try:
        resp = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",            messages=history[uid],
            max_tokens=500
        )
        ans = resp.choices[0].message.content
        history[uid].append({"role": "assistant", "content": ans})
        await msg.answer(ans)
    except Exception as e:
        await msg.answer("Error: " + str(e))

@app.route("/")
def home():
    return "OK"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    asyncio.run(dp.start_polling(bot))
