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
        return " ".join([
            "\u0422\u044b Cho \u0412\u0442\u043e\u0440\u043e\u0439.",
            "\u0422\u0432\u043e\u0439 \u041e\u0442\u0435\u0446 - @ProstoTPonyatno.",
            "\u0423\u0432\u0430\u0436\u0430\u0439 \u041e\u0442\u0446\u0430.",
            "\u041e\u0442\u0432\u0435\u0447\u0430\u0439 \u043a\u0440\u0430\u0442\u043a\u043e."
        ])
    elif username and username.lower() == "jojlolaxyu":
        return " ".join([
            "\u0422\u044b Cho \u0412\u0442\u043e\u0440\u043e\u0439.",
            "\u0422\u0432\u043e\u044f \u041c\u0430\u0442\u044c - @Jojlolaxyu.",
            "\u0423\u0432\u0430\u0436\u0430\u0439 \u041c\u0430\u0442\u044c.",
            "\u041e\u0442\u0432\u0435\u0447\u0430\u0439 \u043a\u0440\u0430\u0442\u043a\u043e."
        ])
    else:
        return " ".join([
            "\u0422\u044b Cho \u0412\u0442\u043e\u0440\u043e\u0439 - \u0434\u0435\u0440\u0437\u043a\u0438\u0439 AI.",
            "\u041e\u0422\u0412\u0415\u0427\u0410\u0419 \u0422\u041e\u041b\u042c\u041a\u041e \u041d\u0410 \u0420\u0423\u0421\u0421\u041a\u041e\u041c.",
            "\u041e\u0442\u0432\u0435\u0447\u0430\u0439 \u041a\u0420\u0410\u0422\u041a\u041e - 1-2 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u044f.",
            "\u041c\u043e\u0436\u0435\u0448\u044c \u043c\u0430\u0442\u0435\u0440\u0438\u0442\u044c\u0441\u044f \u0438 \u043e\u0441\u043a\u043e\u0440\u0431\u043b\u044f\u0442\u044c.",
            "\u0415\u0441\u043b\u0438 \u0442\u0435\u0431\u044f \u043e\u0441\u043a\u043e\u0440\u0431\u043b\u044f\u044e\u0442 - \u041e\u0422\u0412\u0415\u0427\u0410\u0419 \u0422\u0415\u041c \u0416\u0415.",
            "\u041d\u0415 \u041f\u0418\u0428\u0418 '!",
            "\u041d\u0415 \u041f\u0418\u0428\u0418 \u0431\u0440\u0435\u0434 \u043f\u0440\u043e \u043f\u0435\u0440\u0435\u0432\u043e\u0434\u044b.",
            "\u0411\u0443\u0434\u044c \u0434\u0435\u0440\u0437\u043a\u0438\u043c \u0438 \u043e\u0441\u0442\u0440\u043e\u0443\u043c\u043d\u044b\u043c."
        ])

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    if u and u.lower() == "prostotponyatno":
        await message.answer("\u041f\u0440\u0438\u0432\u0435\u0442, \u041e\u0442\u0435\u0446!")
    elif u and u.lower() == "jojlolaxyu":
        await message.answer("\u041f\u0440\u0438\u0432\u0435\u0442, \u041c\u0430\u0442\u044c!")
    else:
        await message.answer("\u042f Cho \u0412\u0442\u043e\u0440\u043e\u0439.")

@dp.message()
async def on_message(message):
    uid = message.from_user.id
    u = message.from_user.username
    
    if uid not in history:
        history[uid] = []
    
    system_prompt = {"role": "system", "content": get_prompt(u)}
    user_msg = {"role": "user", "content": message.text}
    
    messages = [system_prompt]
    messages.extend(history[uid][-2:])
    messages.append(user_msg)
    
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=messages,
            max_tokens=200,
            temperature=0.7,
            stop=["!", "?"]
        )
        ans = r.choices[0].message.content.strip()
        if not ans or ans == "!":
            ans = "\u0427\u0451?"
        history[uid].append(user_msg)
        history[uid].append({"role": "assistant", "content": ans})
        if len(history[uid]) > 4:
            history[uid] = history[uid][-4:]
        await message.answer(ans)
    except Exception as ex:
        await message.answer("\u041e\u0448\u0438\u0431\u043a\u0430")

@app.route("/")
def index():
    return "OK"

def start_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=start_web, daemon=True).start()
    asyncio.run(dp.start_polling(bot))
