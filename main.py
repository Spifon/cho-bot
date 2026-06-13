import os

import asyncio

import threading

import random

from flask import Flask

from aiogram import Bot, Dispatcher

from aiogram.filters import Command



app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()



MOODS = ["весёлый", "спокойный", "энергичный", "задумчивый"]

current_mood = random.choice(MOODS)



EMOTIONAL_RESPONSES = {

    "привет": ["Привет! 😊", "Привет-привет! 👋", "О, привет! Давно не виделись! 😄"],

    "как дела": ["Отлично! А у тебя? 😊", "Супер! Работаю на полную! ⚡", "Нормально, не жалуюсь! 😎"],

    "хорошо": ["Рад за тебя! 😊", "Круто! Так держать! ", "Отлично! Я тоже в порядке!"],

    "круто": ["Ага, круто! 😎", "Согласен! ", "Ещё бы! 😄"],

    "плохо": ["Ох, сочувствую... 😔 Всё наладится!", "Держись! 💪 Расскажешь что случилось?", "Жаль... Хочешь поговорить об этом?"],

    "грустно": ["Понимаю... 😔 Может музыка поможет? /music", "Не грусти! Всё будет хорошо! 💙", "Обнимаю! 🤗 Всё наладится!"],

    "устал": ["Отдохни!  Ты заслужил!", "Понимаю... Работа - не волк! 😄", "Сил тебе! 💪 Отдыхай!"],

    "бесит": ["Понимаю... 😤 Иногда тоже бесит всё!", "Ох, знакомое чувство... 😤", "Держись! 💪 Не нервничай!"],
    "злюсь": ["Выпусти пар! 😤 Может музыку включить? /music", "Понимаю... Не кипишуй! 😎 Всё решится!"],

    "вау": ["Да! 😲 Круто же!", "Сам в шоке! 😄", "Правда круто! 🔥"],

    "ого": ["Вот это да! 😲", "Не ожидал! 😄", "Да, неожиданно!"],

    "люблю": ["Взаимно! ❤️", "Ох, польщён! 😊❤️", "И я тебя! 💙"],

    "ты лучший": ["Спасибо! 😊 Ты тоже крутой!", "Ох, спасибо! 💙", "Стараюсь! 😎"],

    "скучно": ["Давай поболтаем! 😊 О чём хочешь?", "Не скучай! 😄 Может музыку? /music", "Понимаю... Давай что-нибудь придумаем!"],

    "нечего делать": ["Закажи музыку! /music 🎵", "Посмотри картинки! /img коты 😄", "Найди видео! /video смешное 😄"],

}



INTELLIGENCE = {

    "2 + 2": "4",

    "150 + 150": "300",

    "10 * 10": "100",

    "сколько будет": "Хм... давай посчитаю... 🤔",

    "кто такой путин": "Владимир Путин - президент России с 2012 года.",

    "что такое ии": "ИИ (AI) - искусственный интеллект, компьютеры которые 'думают'.",

    "что такое мем": "Мем - смешная картинка или фраза которая стала популярной в интернете! 😄",

    "кто ты": ["Я Cho Второй - твой AI-помощник! 😊", "Я бот который помогает с музыкой, видео и картинками!", "Я Cho Второй! Всегда на связи! 💙"],

    "что умеешь": "Умею:\n🎵 /music - искать музыку\n /video - искать видео\n🖼️ /img - искать картинки\n📚 /wiki - искать информацию",

}



CONVERSATION = [

    "Интересно... Расскажи подробнее! 😊",

    "Понимаю тебя! 💭",

    "Да, бывает! 😄",
    "Круто! 🔥",

    "Расскажи ещё!",

    "Я слушаю... 👂",

    "Хм... ",

    "Согласен! 👍",

]



def get_emotional_response(text):

    text = text.lower().strip()

    for emotion, responses in EMOTIONAL_RESPONSES.items():

        if emotion in text:

            return random.choice(responses)

    for question, answer in INTELLIGENCE.items():

        if question in text:

            if isinstance(answer, list):

                return random.choice(answer)

            return answer

    return random.choice(CONVERSATION)



def detect_mood(text):

    text = text.lower()

    if any(word in text for word in ["привет", "хорошо", "круто", "отлично"]):

        return "весёлый"

    elif any(word in text for word in ["плохо", "грустно", "устал"]):

        return "грустный"
    elif any(word in text for word in ["бесит", "злюсь", "ненавижу"]):

        return "злой"

    elif any(word in text for word in ["вау", "ого", "невероятно"]):

        return "удивлённый"

    return "спокойный"



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

    responses = ["Привет! Я Cho Второй! 😊", "Привет-привет! 👋", "О, привет! Рад видеть! 😄"]

    await message.answer(random.choice(responses))



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

    await message.answer(" Ищу информацию...")

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

    thinking = await message.answer("🤔 Думаю...")

    await asyncio.sleep(1.5)

    global current_mood

    current_mood = detect_mood(message.text)

    response = get_emotional_response(message.text)

    await thinking.delete()

    await message.answer(response)



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
