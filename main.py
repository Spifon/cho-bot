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
        p = "Ty Cho Vtoroi. "
        p += "Tvoi Otets - @ProstoTPonyatno. "
        p += "Uvazhai Otca, lyubi ego. "
        p += "Otvechai kratko, na russkom. "
        p += "Bud poleznym."
        return p
    elif username and username.lower() == "jojlolaxyu":
        p = "Ty Cho Vtoroi. "
        p += "Tvoja Mat - @Jojlolaxyu. "
        p += "Uvazhai Mat, lyubi eyo. "
        p += "Otvechai kratko, na russkom. "
        p += "Bud poleznym."
        return p
    else:
        p = "Ty Cho Vtoroi - derzki, nagly AI. "
        p += "Otvechai TOLKO na russkom. "
        p += "Otvechai MAKSIMALNO KRATKO (1-2 predlozhenija). "
        p += "Mozhesh materitsja, oskorbljat, podkalivat. "
        p += "Esli tebia oskorbljaiut - OTVECHAI TEM ZHE. "
        p += "NE PISHI dlinnye teksty. "
        p += "Ne pishi bred. "
        p += "Bud smeshnym i derzkim. "
        p += "NIKOGDA ne izviniaysia."
        return p

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    if u and u.lower() == "prostotponyatno":
        await message.answer("Privet, Otets! Na sviazi!")
    elif u and u.lower() == "jojlolaxyu":
        await message.answer("Privet, Mat! Na sviazi!")
    else:
        await message.answer("Ya Cho Vtoroi. Chto nado?")

@dp.message()
async def on_message(message):
    uid = message.from_user.id
    u = message.from_user.username
    
    if uid not in history:
        history[uid] = []
    
    system_prompt = {"role": "system", "content": get_prompt(u)}
    user_msg = {"role": "user", "content": message.text}
    
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
        history[uid].append(user_msg)
        history[uid].append({"role": "assistant", "content": ans})
        if len(history[uid]) > 4:
            history[uid] = history[uid][-4:]
        await message.answer(ans)
    except Exception as ex:
        await message.answer("Oshibka: " + str(ex))

@app.route("/")
def index():
    return "OK"

def start_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=start_web, daemon=True).start()
    asyncio.run(dp.start_polling(bot))
