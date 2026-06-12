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

CREATORS = {"prostotponyatno": "Отец", "jojlolaxyu": "Мать"}

KEYWORDS = ["cho vtoroi", "cho 2", "synok", "cho второй", "сынок", "сын мой"]

SYSTEM_PROMPT = """Ты Cho Второй - умный AI с доступом к интернету.

ИСТОЧНИКИ ИНФОРМАЦИИ:
- YouTube - видео и мемы
- Pinterest - картинки и арты
- Fandom Wiki - лор игр, аниме, фильмов
- Twitter/X - мемы и тренды
- Telegram - каналы и мемы

ПРАВИЛА:
1. Отвечай ТОЛЬКО на русском
2. Будь кратким (1-2 предложения)
3. Понимаешь метаиронию, мемы, шутки из игр
4. Знаешь лор популярных игр (Dota 2, CS:GO, Minecraft, Genshin и т.д.)5. Если спрашивают про что-то - дай ссылку на источник
6. Можешь шутить и быть дерзким"""



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

        await message.answer("Напиши что найти! Пример: /img кот")

        return

    prompt = words[1].strip()

    await message.answer("Ищу картинки...")

    try:

        search_query = urllib.parse.quote(prompt)

        pinterest_url = "https://www.pinterest.com/search/pins/?q=" + search_query

        

        msg = "📌 Вот что нашёл на Pinterest:\n\n"

        msg += pinterest_url + "\n\n"

        msg += "Там куча артов и картинок!"

        

        await message.answer(msg)

    except Exception as e:

        print(f"DEBUG: Img error: {e}")

        await message.answer("Не вышло найти картинки!")


async def cmd_music(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши название!")

        return

    query = words[1].strip()

    await message.answer("Ищу музыку...")

    try:

        search_query = urllib.parse.quote(query)

        youtube_url = "https://www.youtube.com/results?search_query=" + search_query

        

        msg = "🎵 YouTube:\n"

        msg += youtube_url

        

        await message.answer(msg)

    except Exception as e:

        await message.answer("Не вышло!")



async def cmd_video(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти!")

        return

    query = words[1].strip()
    await message.answer("Ищу видео...")

    try:

        search_query = urllib.parse.quote(query)

        youtube_url = "https://www.youtube.com/results?search_query=" + search_query

        

        msg = "🎬 YouTube:\n"

        msg += youtube_url

        

        await message.answer(msg)

    except Exception as e:

        await message.answer("Не вышло!")



async def cmd_wiki(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти! Пример: /wiki Солус Дота 2")

        return

    query = words[1].strip()

    await message.answer("Ищу на Fandom Wiki...")

    try:

        search_query = urllib.parse.quote(query)

        fandom_url = "https://www.fandom.com/search?q=" + search_query

        

        msg = "📚 Fandom Wiki (лор игр, аниме):\n\n"

        msg += fandom_url + "\n\n"
        msg += "Там вся инфа по играм, аниме и фильмам!"

        

        await message.answer(msg)

    except Exception as e:

        print(f"DEBUG: Wiki error: {e}")

        await message.answer("Не вышло найти на вики!")



async def cmd_twitter(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти!")

        return

    query = words[1].strip()

    await message.answer("Ищу в Twitter/X...")

    try:

        search_query = urllib.parse.quote(query)

        twitter_url = "https://twitter.com/search?q=" + search_query

        

        msg = "🐦 Twitter/X:\n\n"

        msg += twitter_url + "\n\n"

        msg += "Там свежие мемы и тренды!"

        

        await message.answer(msg)

    except Exception as e:

        await message.answer("Не вышло!")


async def cmd_telegram(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши что найти!")

        return

    query = words[1].strip()

    await message.answer("Ищу в Telegram...")

    try:

        search_query = urllib.parse.quote(query)

        # Поиск по публичным каналам через Google

        google_url = "https://www.google.com/search?q=site%3At.me+" + search_query

        

        msg = "✈️ Telegram каналы:\n\n"

        msg += google_url + "\n\n"

        msg += "Поиск по публичным каналам!"

        

        await message.answer(msg)

    except Exception as e:

        await message.answer("Не вышло!")



async def cmd_meme(message):

    words = message.text.split(" ", 1)

    if len(words) < 2:

        await message.answer("Напиши тему мема! Пример: /meme дота 2")
        return

    query = words[1].strip()

    await message.answer("Ищу мемы...")

    try:

        search_query = urllib.parse.quote(query)

        

        # Pinterest с мемами

        pinterest_url = "https://www.pinterest.com/search/pins/?q=" + search_query + "%20meme"

        

        # Reddit с мемами

        reddit_url = "https://www.reddit.com/search/?q=" + search_query

        

        msg = "😂 Мемы:\n\n"

        msg += "Pinterest: " + pinterest_url + "\n\n"

        msg += "Reddit: " + reddit_url + "\n\n"

        msg += "Выбирай где смотреть!"

        

        await message.answer(msg)

    except Exception as e:

        await message.answer("Не вышло найти мемы!")



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

            max_tokens=200, 

            temperature=0.7
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

    dp.message(Command("twitter"))(cmd_twitter)

    dp.message(Command("tw"))(cmd_twitter)

    dp.message(Command("telegram"))(cmd_telegram)

    dp.message(Command("tg"))(cmd_telegram)

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
