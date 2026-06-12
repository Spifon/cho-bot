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

SYSTEM_PROMPT = "Ты Cho Второй. Отвечай ТОЛЬКО на русском. Будь кратким."



def get_user_prompt(username):

    result = "Собеседник обычный. Будь дерзким."

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

        await message.answer("Напиши что нарисовать! Пример: /img кот")

        return

    prompt = words[1].strip()

    await message.answer("Рисую...")

    try:

        # Кодируем для URL

        safe_prompt = prompt.replace(" ", "%20")

        img_url = "https://image.pollinations.ai/prompt/" + safe_prompt + "?width=1024&height=1024&nologo=true"

        print(f"DEBUG: Sending image URL: {img_url}")

        await message.answer_photo(photo=img_url, caption=prompt)

        print("DEBUG: Image sent successfully")

    except Exception as e:

        print(f"DEBUG: Image error: {e}")

        await message.answer("Не вышло нарисовать! Попробуй другой запрос.")



async def cmd_music(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши название! Пример: /music Imagine Dragons")

        return

    query = words[1].strip()

    await message.answer("Ищу музыку...")
    try:

        # Ищем на YouTube

        search_query = urllib.parse.quote(query)

        youtube_url = "https://www.youtube.com/results?search_query=" + search_query

        

        msg = "🎵 Вот что нашёл:\n\n"

        msg += youtube_url + "\n\n"

        msg += "Скачай музыку оттуда или послушай онлайн!"

        

        await message.answer(msg)

        print("DEBUG: Music search sent")

    except Exception as e:

        print(f"DEBUG: Music error: {e}")

        await message.answer("Не вышло найти музыку!")



async def cmd_video(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти! Пример: /video котики")

        return

    query = words[1].strip()

    await message.answer("Ищу видео...")

    try:

        # Ищем на YouTube

        search_query = urllib.parse.quote(query)
        youtube_url = "https://www.youtube.com/results?search_query=" + search_query

        

        msg = "🎬 Вот что нашёл:\n\n"

        msg += youtube_url + "\n\n"

        msg += "Смотри видео на YouTube!"

        

        await message.answer(msg)

        print("DEBUG: Video search sent")

    except Exception as e:

        print(f"DEBUG: Video error: {e}")

        await message.answer("Не вышло найти видео!")



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

        print("DEBUG: Message sent successfully")

    except Exception as e:

        print(f"DEBUG: AI error: {e}")

        await message.answer("Ошибка")



def register_handlers():

    dp.message(Command("start"))(cmd_start)
    dp.message(Command("img"))(cmd_img)

    dp.message(Command("music"))(cmd_music)

    dp.message(Command("video"))(cmd_video)

    dp.message()(on_message)



@app.route("/")

def index():

    return "OK"



def start_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)



if __name__ == "__main__":

    register_handlers()

    print("DEBUG: бот запускается...")

    t = threading.Thread(target=start_web, daemon=True)

    t.start()

    asyncio.run(dp.start_polling(bot))
