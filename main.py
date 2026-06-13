import os

import asyncio

import threading

import urllib.parse

from flask import Flask

from aiogram import Bot, Dispatcher

from aiogram.filters import Command



app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

chat_history = {}

CREATORS = {"prostotponyatno": "Отец", "jojlolaxyu": "Мать"}

KEYWORDS = ["cho vtoroi", "cho 2", "synok", "cho второй", "сынок", "сын мой"]



# ПРОСТЫЕ ОТВЕТЫ

SIMPLE_RESPONSES = {

    "привет": "Привет! Я Cho Второй. Спрашивай что хочешь!",

    "как дела": "Хорошо! Работаю как часы ⚙️",

    "кто ты": "Я Cho Второй - твой AI-помощник. Помогаю с информацией, музыкой и картинками!",

    "что умеешь": "Умею:\n🎵 Искать музыку /music\n🎬 Искать видео /video\n🖼️ Искать картинки /img\n📚 Искать инфо /wiki",

}



def get_user_prompt(username):
    result = ""

    if username and username.lower() in CREATORS:

        role = CREATORS[username.lower()]

        result = "Привет, " + role + "!"

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

        await message.answer("Напиши что найти! Пример: /img кот")

        return

    query = words[1].strip()

    await message.answer("🖼️ Ищу картинки...")

    short_query = query.replace(" ", "+")

    pinterest_url = "https://pinterest.com/search/pins/?q=" + short_query

    await message.answer("Pinterest:\n" + pinterest_url)



async def cmd_music(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши название! Пример: /music Imagine Dragons")

        return

    query = words[1].strip()

    await message.answer("🎵 Ищу музыку...")

    short_query = query.replace(" ", "+")

    youtube_url = "https://youtube.com/results?search_query=" + short_query

    await message.answer("YouTube:\n" + youtube_url)


async def cmd_video(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти! Пример: /video котики")

        return

    query = words[1].strip()

    await message.answer("🎬 Ищу видео...")

    short_query = query.replace(" ", "+")

    youtube_url = "https://youtube.com/results?search_query=" + short_query

    await message.answer("YouTube:\n" + youtube_url)



async def cmd_wiki(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти!")

        return

    query = words[1].strip()

    await message.answer("📚 Ищу информацию...")

    short_query = query.replace(" ", "+")

    fandom_url = "https://fandom.com/search?q=" + short_query

    wiki_url = "https://ru.wikipedia.org/wiki/Служебная:Поиск?search=" + short_query

    msg = "Поиск:\n\nFandom: " + fandom_url + "\n\nWikipedia: " + wiki_url

    await message.answer(msg)



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

    

    # ЭФФЕКТ "ДУМАЮ"

    thinking = await message.answer("🤔 Думаю...")

    await asyncio.sleep(1)

    

    text = message.text.lower()

    

    # ПРОВЕРЯЕМ ПРОСТЫЕ ОТВЕТЫ

    for key, response in SIMPLE_RESPONSES.items():

        if key in text:

            await thinking.delete()

            await message.answer(response)

            return

    

    # ПРОВЕРЯЕМ КТО ОБРАЩАЕТСЯ

    username = message.from_user.username
    greeting = get_user_prompt(username)

    

    # ПРОСТОЙ ОТВЕТ

    await thinking.delete()

    if greeting:

        await message.answer(greeting + " Чем помочь?")

    else:

        await message.answer("Чем могу помочь? Используй команды:\n/music - музыка\n/video - видео\n/img - картинки\n/wiki - информация")



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
