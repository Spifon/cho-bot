import os

import asyncio

import threading

import urllib.parse

from flask import Flask

from aiogram import Bot, Dispatcher

from aiogram.filters import Command

from openai import OpenAI

import yt_dlp



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

    print(f"DEBUG: тип={message.chat.type}, текст={message.text}")

    if message.chat.type == "private":

        print("DEBUG: личка - отвечаю")

        return True

    if message.text:

        text = message.text.lower()

        for keyword in KEYWORDS:

            if keyword in text:

                print(f"DEBUG: найдено {keyword} - отвечаю")

                return True

    if message.reply_to_message:

        if message.reply_to_message.from_user.id == bot_id:

            print("DEBUG: ответ боту - отвечаю")

            return True

    print("DEBUG: не отвечаю")

    return False



async def cmd_start(message):

    print(f"DEBUG: /start от {message.from_user.username}")

    u = message.from_user.username

    answer = "Привет! Я Cho Второй."
    if u and u.lower() == "prostotponyatno":

        answer = "Привет, Отец!"

    if u and u.lower() == "jojlolaxyu":

        answer = "Привет, Мать!"

    await message.answer(answer)



async def cmd_img(message):

    print(f"DEBUG: /img от {message.from_user.username}")

    words = message.text.split()

    if len(words) < 2:

        await message.answer("Напиши что нарисовать!")

        return

    prompt = words[1]

    await message.answer("Рисую...")

    try:

        encoded = urllib.parse.quote(prompt)

        img_url = "https://image.pollinations.ai/prompt/" + encoded + "?width=1024&height=1024"

        await message.answer_photo(photo=img_url, caption="Готово")

    except Exception as e:

        print(f"DEBUG: ошибка картинки: {e}")

        await message.answer("Не вышло!")



async def cmd_music(message):

    print(f"DEBUG: /music от {message.from_user.username}")

    words = message.text.split(" ", 1)
    if len(words) < 2:

        await message.answer("Напиши название песни! Пример: /music Imagine Dragons")

        return

    query = words[1].strip()

    await message.answer("Ищу музыку...")

    try:

        ydl_opts = {

            'format': 'bestaudio/best',

            'outtmpl': '%(title)s.%(ext)s',

            'quiet': True,

            'no_warnings': True

        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(f"ytsearch:{query}", download=False)

            if info and 'entries' in info and len(info['entries']) > 0:

                video = info['entries'][0]

                video_url = video['url']

                title = video['title']

                await message.answer_audio(audio=video_url, caption=f"🎵 {title}")

                print(f"DEBUG: музыка отправлена: {title}")

            else:

                await message.answer("Не нашёл такую песню!")

    except Exception as e:

        print(f"DEBUG: ошибка музыки: {e}")

        await message.answer("Не вышло скачать музыку!")


async def on_message(message):

    print(f"DEBUG: получено сообщение в {message.chat.type}")

    try:

        me = await bot.get_me()

        bot_id = me.id

        print(f"DEBUG: bot_id={bot_id}")

    except Exception as e:

        print(f"DEBUG: ошибка get_me: {e}")

        return

    respond = should_respond(message, bot_id)

    if not respond:

        print("DEBUG: should_respond=False")

        return

    print("DEBUG: обрабатываю...")

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

        print("DEBUG: отправлено успешно")

    except Exception as e:

        print(f"DEBUG: ошибка AI: {e}")

        await message.answer("Ошибка")



def register_handlers():

    dp.message(Command("start"))(cmd_start)

    dp.message(Command("img"))(cmd_img)

    dp.message(Command("music"))(cmd_music)

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
