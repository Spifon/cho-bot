import os

import asyncio

import threading

import urllib.parse

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

chat_history = {}

CREATORS = {"prostotponyatno": "Otets", "jojlolaxyu": "Mat"}

KEYWORDS = ["cho vtoroi", "cho 2", "synok"]

SYSTEM_PROMPT = "You are Cho Vtoroi. Answer ONLY in Russian. Be brief."



def get_user_prompt(username):

    result = "Your partner is regular user. Be cheeky."

    if username and username.lower() in CREATORS:

        role = CREATORS[username.lower()]

        result = "Your partner is your " + role + ". Respect them."
    return result



def should_respond(message, bot_id):

    result = False

    if message.chat.type == "private":

        result = True

    if message.text:

        text = message.text.lower()

        for keyword in KEYWORDS:

            if keyword in text:

                result = True

    if message.reply_to_message:

        if message.reply_to_message.from_user.id == bot_id:

            result = True

    return result



async def cmd_start(message):

    u = message.from_user.username

    answer = "Privet! Ya Cho Vtoroi."

    if u and u.lower() == "prostotponyatno":

        answer = "Privet Otets!"

    if u and u.lower() == "jojlolaxyu":

        answer = "Privet Mat!"

    await message.answer(answer)


async def cmd_img(message):

    words = message.text.split()

    if len(words) < 2:

        await message.answer("Napishi chto narisovat!")

        return

    prompt = words[1]

    await message.answer("Risuyu...")

    try:

        encoded = urllib.parse.quote(prompt)

        img_url = "https://image.pollinations.ai/prompt/" + encoded + "?width=1024&height=1024"

        await message.answer_photo(photo=img_url, caption="Gotovo")

    except Exception:

        await message.answer("Ne vyshlo!")



async def on_message(message):

    me = await bot.me

    bot_id = me.id

    respond = should_respond(message, bot_id)

    if not respond:

        return

    chat_id = message.chat.id

    username = message.from_user.username

    if chat_id not in chat_history:

        chat_history[chat_id] = []

    messages = []
    messages.append({"role": "system", "content": SYSTEM_PROMPT})

    user_prompt = get_user_prompt(username)

    messages.append({"role": "system", "content": user_prompt})

    if chat_history[chat_id]:

        last_msgs = chat_history[chat_id][-3:]

        for msg in last_msgs:

            messages.append(msg)

    messages.append({"role": "user", "content": message.text})

    try:

        r = client.chat.completions.create(model="meta-llama/llama-3-8b-instruct", messages=messages, max_tokens=200, temperature=0.8)

        ans = r.choices[0].message.content.strip()

        chat_history[chat_id].append({"role": "user", "content": message.text})

        chat_history[chat_id].append({"role": "assistant", "content": ans})

        if len(chat_history[chat_id]) > 6:

            chat_history[chat_id] = chat_history[chat_id][-6:]

        await message.answer(ans)

    except Exception:

        await message.answer("Oshibka")



def register_handlers():

    dp.message(Command("start"))(cmd_start)

    dp.message(Command("img"))(cmd_img)

    dp.message()(on_message)



@app.route("/")
def index():

    return "OK"



def start_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)



if __name__ == "__main__":

    register_handlers()

    t = threading.Thread(target=start_web, daemon=True)

    t.start()

    asyncio.run(dp.start_polling(bot))
