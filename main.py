import os

import asyncio

import threading

import urllib.parse

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

CREATORS = {"prostotponyatno": "Отец", "jojlolaxyu": "Мать"}

KEYWORDS = ["cho vtoroi", "cho 2", "synok", "cho второй", "сынок", "сын мой"]

SYSTEM_PROMPT = """Ты Cho Второй - AI-помощник.

ПРАВИЛА:
1. Отвечай ТОЛЬКО на русском
2. Будь кратким (1-2 предложения)
3. Отвечай ПО ДЕЛУ, не выдумывай
4. НЕ ИЩИ мемы в обычных словах
5. Если не знаешь ответа - скажи "Не знаю"

ИНФОРМАЦИЯ:
- V1, V2 - персонажи из ULTRAKILL
- Обычные слова - это НЕ мемы
БУДЬ СПОКОЙНЫМ И АДЕКВАТНЫМ!"""



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

        await message.answer("Напиши что нарисовать!")

        return

    prompt = words[1].strip()

    await message.answer("Рисую...")

    try:

        safe_prompt = prompt.replace(" ", "_").replace("!", "").replace("?", "")

        img_url = "https://image.pollinations.ai/prompt/" + safe_prompt + "?width=1024&height=1024&nologo=true&seed=42"

        

        async with aiohttp.ClientSession() as session:

            async with session.get(img_url, timeout=10) as resp:

                if resp.status == 200:

                    await message.answer_photo(photo=img_url, caption=prompt)

                else:

                    await message.answer("Не вышло. Попробуй проще.")

    except Exception as e:

        print(f"DEBUG: Img error: {e}")
        await message.answer("Не вышло!")



async def cmd_music(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши название!")

        return

    query = words[1].strip()

    await message.answer("Ищу музыку...")

    youtube_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)

    await message.answer("🎵 YouTube:\n" + youtube_url)



async def cmd_video(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти!")

        return

    query = words[1].strip()

    await message.answer("Ищу видео...")

    youtube_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)

    await message.answer("🎬 YouTube:\n" + youtube_url)



async def cmd_wiki(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:
        await message.answer("Напиши что найти!")

        return

    query = words[1].strip().lower()

    await message.answer("Ищу информацию...")

    

    wikis = {

        "ultrakill": "https://ultrakill.fandom.com",

        "v1": "https://ultrakill.fandom.com/wiki/V1",

        "v2": "https://ultrakill.fandom.com/wiki/V2",

        "gabriel": "https://ultrakill.fandom.com/wiki/Gabriel",

        "dota": "https://dota2.fandom.com/ru",

        "genshin": "https://genshin.fandom.com/ru",

        "minecraft": "https://minecraft.fandom.com/ru"

    }

    

    found_url = None

    for key, url in wikis.items():

        if key in query:

            found_url = url

            break

    

    if found_url:

        await message.answer("📚 Вот что нашёл:\n\n" + found_url)

    else:

        search_url = "https://www.fandom.com/search?q=" + urllib.parse.quote(query)
        await message.answer("📚 Поищи здесь:\n\n" + search_url)



async def cmd_meme(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши тему!")

        return

    query = words[1].strip()

    await message.answer("Ищу мемы...")

    pinterest_url = "https://www.pinterest.com/search/pins/?q=" + urllib.parse.quote(query) + "%20meme"

    await message.answer("😂 Pinterest:\n" + pinterest_url)



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

        r = client.chat.completions.create(

            model="meta-llama/llama-3-8b-instruct", 

            messages=messages, 

            max_tokens=150, 

            temperature=0.5

        )

        ans = r.choices[0].message.content.strip()

        chat_history[chat_id].append({"role": "user", "content": message.text})

        chat_history[chat_id].append({"role": "assistant", "content": ans})

        if len(chat_history[chat_id]) > 6:

            chat_history[chat_id] = chat_history[chat_id][-6:]

        await message.answer(ans)

    except Exception as e:

        print(f"DEBUG: AI error: {e}")
        await message.answer("Ошибка")



def register_handlers():

    dp.message(Command("start"))(cmd_start)

    dp.message(Command("img"))(cmd_img)

    dp.message(Command("music"))(cmd_music)

    dp.message(Command("video"))(cmd_video)

    dp.message(Command("wiki"))(cmd_wiki)

    dp.message(Command("meme"))(cmd_meme)

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

            print("DEBUG: Перезапускаю через 5 секунд...")

            await asyncio.sleep(5)



if __name__ == "__main__":

    register_handlers()

    print("DEBUG: бот запускается...")

    t = threading.Thread(target=start_web, daemon=True)

    t.start()

    asyncio.run(polling_with_restart())
