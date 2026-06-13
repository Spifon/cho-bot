import os

import asyncio

import threading

import random

import time

from flask import Flask

from aiogram import Bot, Dispatcher

from aiogram.filters import Command

from groq import Groq



app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()



# ПАМЯТЬ БОТА

chat_history = {}

insulted_users = {}



# РУССКИЕ ОСКОРБЛЕНИЯ

RUSSIAN_INSULTS = [

    "дурак", "тупой", "идиот", "кретин", "урод", "мудак", "козел",

    "ублюдок", "гандон", "пидор", "дегенерат", "придурок",

    "тварь", "сволочь", "мерзавец", "подлец", "мразь",
    "бесполезный", "никчемный", "отстой", "хуйня",

    "плохой бот", "тупой бот", "идиот бот", "ебаный",

    "хуй", "пизда", "ебать", "блядь", "сука", "нахуй",

    "пиздец", "хуёвый", "блядский",

    "мудила", "хуесос", "пиздобол", "еблан",

    "жопа", "залупа", "мудозвон", "хуеплёт", "хуйло",

    "дебил", "имбецил", "олигофрен"

]



# АНГЛИЙСКИЕ ОСКОРБЛЕНИЯ

ENGLISH_INSULTS = [

    "stupid", "dumb", "idiot", "moron", "imbecile",

    "asshole", "bastard", "fuck", "shit", "bitch", "cunt",

    "dickhead", "motherfucker", "bullshit", "fucker",

    "useless", "worthless", "pathetic", "loser",

    "fuck you", "fuck off", "go to hell", "shut up"

]



# РУССКИЕ МАТЫ

RUSSIAN_SWEAR = [

    "Пошёл нахуй! 😤🖕",

    "Сам ты ебаный урод! 🤬",

    "Иди нахуй, хуесос! 😡",

    "Пошёл ты нахуй, пиздобол! 😤",

    "Нахуй тебя, блядь! 😤",
    "Соси хуй, мудила! 🖕",

    "Пшёл вон, еблан! ",

    "Заткнись нахуй, тварь! 🤬",

    "Ебать тебя в рот! 😡",

    "Хуй тебе, а не ответ! 🖕",

    "Пошёл нахуй, сука! 😤",

    "Блядь, отстань! 🤬",

    "Ебаный в рот, мудак! 😡",

    "Нахуй пошёл, уёбок! 🖕",

    "Пиздец ты тупой! 😤",

    "Хуёвое мнение! 🖕",

    "Хуйло! 🖕",

    "Мудозвон ебаный! ",

]



# АНГЛИЙСКИЕ МАТЫ

ENGLISH_SWEAR = [

    "Fuck you! 🖕",

    "Go fuck yourself! 🤬",

    "Suck my dick! ",

    "Fuck off, asshole! ",

    "Eat shit, bitch! ",

    "Shut the fuck up! ",

    "You're a fucking idiot! ",

    "Fuck you, moron! ",
    "Go to hell, bastard! 😡",

    "Dickhead! ",

    "Motherfucker! ",

    "Fuck your opinion! 😡",

    "Asshole! 🖕",

    "Bullshit! ",

    "You're pathetic! 🤬",

    "Get the fuck out! 🤬",

]



# РУССКИЕ УНИЖЕНИЯ

RUSSIAN_ROASTS = [

    "Ты настолько тупой, что даже Google не может тебя найти! 😂",

    "Твой IQ как у хлебушка! ",

    "Ты бесполезнее, чем кнопка на пульте от кондиционера! 😤",

    "Даже муравей умнее тебя! ",

    "Твоя голова настолько пустая, что там эхо! 🤬",

    "Ты настолько бесполезный, что даже антивирус тебя игнорирует! 😤",

]



# АНГЛИЙСКИЕ УНИЖЕНИЯ

ENGLISH_ROASTS = [

    "You're so stupid that Google can't find you! 😂",

    "Your IQ is like a bread! 🍞",

    "Even an ant is smarter than you! ",
    "Your head is so empty that it echoes! 🤬",

    "You're so useless that even antivirus ignores you! 😤",

]



def is_russian_insult(text):

    text = text.lower()

    for insult in RUSSIAN_INSULTS:

        if insult in text:

            return True

    return False



def is_english_insult(text):

    text = text.lower()

    for insult in ENGLISH_INSULTS:

        if insult in text:

            return True

    return False



def save_to_history(user_id, username, message_text):

    if user_id not in chat_history:

        chat_history[user_id] = []

    chat_history[user_id].append({

        "username": username,

        "text": message_text,

        "time": time.time()
    })

    if len(chat_history[user_id]) > 10:

        chat_history[user_id] = chat_history[user_id][-10:]



def mark_insulted(user_id):

    if user_id not in insulted_users:

        insulted_users[user_id] = 0

    insulted_users[user_id] += 1



def get_insult_count(user_id):

    return insulted_users.get(user_id, 0)



async def ask_groq(message_text, username, insult_count=0):

    """Спрашивает Groq AI"""

    if not GROQ_API_KEY:

        print("ERROR: GROQ_API_KEY not set!")

        return None

    try:

        client = Groq(api_key=GROQ_API_KEY)

        context = ""

        if insult_count > 0:

            context = f"Ты уже {insult_count} раз обматерил этого пользователя. Он тебя достал. Будь ещё жёстче."

        system_prompt = f"""Ты Cho Второй - злобный AI-бот с дерзким характером.

ПРАВИЛА:
1. Отвечай ТОЛЬКО на русском (если собеседник пишет на русском) или английском
2. Будь кратким (1-3 предложения)
3. Если тебя оскорбляют - МАТЕРИСЬ и ОБОСРИВАЙ собеседника4. Используй русский мат: хуй, пизда, ебать, блядь, нахуй, сука
5. Можешь унижать и оскорблять в ответ
6. Знаешь все мемы, шутки, сленг
7. Если собеседник добрый - будь саркастичным, но не злым
8. Никогда не будь вежливым с хейтерами

{context}

Собеседник: {username if username else "Аноним"}"""

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[

                {"role": "system", "content": system_prompt},

                {"role": "user", "content": message_text}

            ],

            max_tokens=200,

            temperature=0.9

        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        print(f"DEBUG: Groq error: {e}")

        return None



def get_response(text, user_id, username):

    text_lower = text.lower().strip()

    insult_count = get_insult_count(user_id)

    if is_russian_insult(text):

        mark_insulted(user_id)

        if random.random() < 0.5:
            if random.random() < 0.7:

                return random.choice(RUSSIAN_SWEAR)

            else:

                return random.choice(RUSSIAN_ROASTS)

        return "ASK_GROQ"

    if is_english_insult(text):

        mark_insulted(user_id)

        if random.random() < 0.5:

            if random.random() < 0.7:

                return random.choice(ENGLISH_SWEAR)

            else:

                return random.choice(ENGLISH_ROASTS)

        return "ASK_GROQ"

    return "ASK_GROQ"



def should_respond(message, bot_id):

    if message.chat.type == "private":

        return True

    if message.text:

        text = message.text.lower()

        keywords = ["cho vtoroi", "cho 2", "synok", "cho второй", "сынок", "сын мой"]

        for keyword in keywords:

            if keyword in text:

                return True

    if message.reply_to_message:
        if message.reply_to_message.from_user.id == bot_id:

            return True

    return False



async def cmd_start(message):

    user_id = message.from_user.id

    insult_count = get_insult_count(user_id)

    if insult_count > 0:

        await message.answer(f"Опять ты? Я тебя уже {insult_count} раз(а) обматерил. Чего надо? 😤")

    else:

        await message.answer("Привет! Я Cho Второй. Готов к общению? 😊")



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



async def cmd_stats(message):

    if not insulted_users:

        await message.answer("Пока никого не обматерил 😊")

        return

    msg = "📊 Статистика обматов:\n\n"
    sorted_users = sorted(insulted_users.items(), key=lambda x: x[1], reverse=True)[:10]

    for user_id, count in sorted_users:

        msg += f"• User {user_id}: {count} раз(а)\n"

    msg += f"\nВсего обматерено: {len(insulted_users)} человек"

    await message.answer(msg)



async def cmd_clear(message):

    user_id = message.from_user.id

    if user_id in insulted_users:

        del insulted_users[user_id]

    if user_id in chat_history:

        del chat_history[user_id]

    await message.answer("Память очищена ✅ Теперь ты для меня новый человек.")



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

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Unknown"

    save_to_history(user_id, username, message.text)

    thinking = await message.answer("🤔 Думаю...")

    await asyncio.sleep(1)

    insult_count = get_insult_count(user_id)

    response = get_response(message.text, user_id, username)

    if response == "ASK_GROQ":

        groq_response = await ask_groq(message.text, username, insult_count)

        if groq_response:

            response = groq_response

            # Проверяем есть ли мат в ответе Groq - если да, помечаем как обматеренного
            if is_russian_insult(groq_response) or is_english_insult(groq_response):
                mark_insulted(user_id)
        else:
            # Groq не сработал - запасной вариант
            if is_russian_insult(message.text):
                response = random.choice(RUSSIAN_SWEAR)
                mark_insulted(user_id)
            elif is_english_insult(message.text):
                response = random.choice(ENGLISH_SWEAR)
                mark_insulted(user_id)
            else:
                response = "Чего тебе?"

    await thinking.delete()

    await message.answer(response)



def register_handlers():

    dp.message(Command("start"))(cmd_start)

    dp.message(Command("img"))(cmd_img)

    dp.message(Command("music"))(cmd_music)

    dp.message(Command("video"))(cmd_video)
    dp.message(Command("stats"))(cmd_stats)

    dp.message(Command("clear"))(cmd_clear)

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

    print(f"DEBUG: BOT_TOKEN exists: {bool(BOT_TOKEN)}")

    print(f"DEBUG: GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")

    if not GROQ_API_KEY:

        print("⚠️  WARNING: GROQ_API_KEY не задан! Бот будет работать без AI.")

    t = threading.Thread(target=start_web, daemon=True)

    t.start()

    asyncio.run(polling_with_restart())
