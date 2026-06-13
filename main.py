import os

import asyncio

import threading

import urllib.parse

import aiohttp

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

CREATORS = {"prostotponyatno": "Отец", "jojlolaxyu": "Мать"}

KEYWORDS = ["cho vtoroi", "cho 2", "synok", "cho второй", "сынок", "сын мой"]

SYSTEM_PROMPT = "Ты Cho Второй. Отвечай на русском. Будь кратким."



def get_user_prompt(username):

    result = "Собеседник обычный."

    if username and username.lower() in CREATORS:

        role = CREATORS[username.lower()]
        result = "Собеседник твой " + role + ". Уважай его."

    return result



def should_respond(message, bot_id):

    if message.chat.type == "private":

        return True

    if message.text:

        text = message.text.lower()

        for keyword in KEYWORDS:

            if keyword in text:

                return True

    if message.reply_to_message:

        if message.reply_to_message.from_user.id == bot_id:

            return True

    return False



async def cmd_start(message):

    u = message.from_user.username

    answer = "Привет! Я Cho Второй."

    if u and u.lower() == "prostotponyatno":

        answer = "Привет, Отец!"

    if u and u.lower() == "jojlolaxyu":

        answer = "Привет, Мать!"

    await message.answer(answer)


async def cmd_img(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что нарисовать!")

        return

    prompt = words[1].strip()

    await message.answer("Рисую...")

    try:

        safe_prompt = prompt.replace(" ", "_")

        img_url = "https://image.pollinations.ai/prompt/" + safe_prompt + "?width=1024&height=1024&nologo=true"

        await message.answer_photo(photo=img_url, caption=prompt)

    except Exception as e:

        print(f"DEBUG: Img error: {e}")

        await message.answer("Не вышло!")



async def cmd_music(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши название!")

        return

    query = words[1].strip()

    short_query = query.replace(" ", "+")

    youtube_url = "https://youtube.com/results?search_query=" + short_query

    await message.answer("🎵 YouTube:\n" + youtube_url)


async def cmd_video(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти!")

        return

    query = words[1].strip()

    short_query = query.replace(" ", "+")

    youtube_url = "https://youtube.com/results?search_query=" + short_query

    await message.answer("🎬 YouTube:\n" + youtube_url)



async def cmd_wiki(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти!")

        return

    query = words[1].strip().lower()

    wikis = {

        "ultrakill": "https://ultrakill.fandom.com",

        "v1": "https://ultrakill.fandom.com/wiki/V1",

        "v2": "https://ultrakill.fandom.com/wiki/V2",

        "gabriel": "https://ultrakill.fandom.com/wiki/Gabriel",

        "dota": "https://dota2.fandom.com/ru"

    }

    found_url = None

    for key, url in wikis.items():
        if key in query:

            found_url = url

            break

    if found_url:

        await message.answer("📚 " + found_url)

    else:

        short_query = query.replace(" ", "+")

        search_url = "https://fandom.com/search?q=" + short_query

        await message.answer("📚 Fandom:\n" + search_url)



async def on_message(message):

    try:

        me = await bot.get_me()

        bot_id = me.id

    except Exception as e:

        print(f"DEBUG: get_me error: {e}")

        return

    respond = should_respond(message, bot_id)

    if not respond:

        return

    thinking = await message.answer("🤔 Думаю...")

    await asyncio.sleep(1.5)

    chat_id = message.chat.id

    username = message.from_user.username

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    messages = []

    messages.append({"role": "system", "content": SYSTEM_PROMPT})

    messages.append({"role": "system", "content": get_user_prompt(username)})

    if chat_history[chat_id]:

        last_msgs = chat_history[chat_id][-3:]

        for msg in last_msgs:

            messages.append(msg)

    messages.append({"role": "user", "content": message.text})

    try:

        r = client.chat.completions.create(

            model="meta-llama/llama-3.1-8b-instruct:free",

            messages=messages,

            max_tokens=200,

            temperature=0.7

        )

        ans = r.choices[0].message.content.strip()

        chat_history[chat_id].append({"role": "user", "content": message.text})

        chat_history[chat_id].append({"role": "assistant", "content": ans})

        if len(chat_history[chat_id]) > 6:

            chat_history[chat_id] = chat_history[chat_id][-6:]

        await thinking.delete()

        await message.answer(ans)

    except Exception as e:

        print(f"DEBUG: AI error: {e}")
        await thinking.delete()

        await message.answer("⚠️ Ошибка. Попробуй позже.")



def register_handlers():

    dp.message(Command("start"))(cmd_start)

    dp.message(Command("img"))(cmd_img)

    dp.message(Command("music"))(cmd_music)

    dp.message(Command("video"))(cmd_video)

    dp.message(Command("wiki"))(cmd_wiki)

    dp.message()(on_message)



@app.route("/")

def index():

    return "OK"



@app.route("/health")

def health():

    return "OK"



def start_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)



async def polling_with_restart():

    while True:
        try:

            print("DEBUG: Запускаю polling...")

            await dp.start_polling(bot)

        except Exception as e:

            print(f"DEBUG: Polling оборвался: {e}")

            await asyncio.sleep(5)



if __name__ == "__main__":

    register_handlers()

    print("DEBUG: бот запускается...")

    t = threading.Thread(target=start_web, daemon=True)

    t.start()

    asyncio.run(polling_with_restart())
