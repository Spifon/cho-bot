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



# СЕМЬЯ (не матерится на них)

CREATORS = {

    "prostotponyatno": "Отец",

    "jojlolaxyu": "Мать",

    "chocho34562": "Дедушка"

}



# ВСЕ РУССКИЕ МАТЫ И ОСКОРБЛЕНИЯ

INSULTS = [

    "дурак", "тупой", "идиот", "кретин", "урод", "мудак", "козел",

    "ублюдок", "гандон", "пидор", "дегенерат", "придурок",

    "тварь", "сволочь", "мерзавец", "подлец", "мразь",
    "бесполезный", "никчемный", "отстой", "хуйня",

    "плохой бот", "тупой бот", "идиот бот", "ебаный",

    "хуй", "пизда", "ебать", "блядь", "сука", "нахуй",

    "пиздец", "ебаный", "хуёвый", "блядский",

    "мудила", "хуесос", "пиздобол", "еблан",

    "жопа", "залупа", "мудозвон", "хуеплёт",

    "пиздатый", "ебучий", "блядство", "хуйло"

]



# МАТЕРНЫЕ ОТВЕТЫ (ЖЁСТКИЕ)

SWEAR_RESPONSES = [

    "Пошёл нахуй, мудак! 😤🖕",

    "Сам ты ебаный урод! 🤬",

    "Иди нахуй, хуесос! ",

    "Пошёл ты нахуй, пиздобол! ",

    "Нахуй тебя, блядь! 😤",

    "Соси хуй, мудила! 🖕",

    "Пшёл вон, еблан! 😡",

    "Заткнись нахуй, тварь! 🤬",

    "Сам такой, пиздец! 😤",

    "Иди нахуй, дебил! ",

    "Ебать тебя в рот! 😡",

    "Хуй тебе, а не ответ! 🖕",

    "Пошёл нахуй, сука! ",

    "Блядь, отстань! 🤬",
    "Ебаный в рот, мудак! ",

    "Нахуй пошёл, уёбок! 🖕",

    "Пиздец ты тупой! ",

    "Хуёвое мнение! 🖕",

    "Ебать, какой ты мудак! 😡",

    "Блядский идиот! ",

]



# ОСКОРБЛЕНИЯ ДЛЯ ХЕЙТЕРОВ (ДОПОЛНИТЕЛЬНЫЕ)

ROAST_RESPONSES = [

    "Ты настолько тупой, что даже Google не может тебя найти! 😂",

    "Твой IQ как у хлебушка! 🍞",

    "Ты бесполезнее, чем кнопка на пульте от кондиционера! 😤",

    "Даже муравей умнее тебя! ",

    "Ты такой тупой, что думаешь что Wi-Fi это напиток! 😂",

    "Твоя голова настолько пустая, что там эхо! 🤬",

    "Ты настолько бесполезный, что даже антивирус тебя игнорирует! ",

]



# ОБЫЧНЫЕ ОТВЕТЫ (для всех)

EMOTIONAL_RESPONSES = {

    "привет": ["Привет! 😊", "Привет-привет! 👋", "О, привет! 😄"],

    "как дела": ["Отлично! А у тебя? 😊", "Супер! Работаю! ⚡", "Нормально! 😎"],

    "хорошо": ["Рад за тебя! 😊", "Круто! ", "Отлично!"],

    "круто": ["Ага, круто! ", "Согласен! ", "Ещё бы! 😄"],
    "спасибо": ["Пожалуйста! 😊", "Всегда рад! ", "Не за что!"],

    "плохо": ["Сочувствую... 😔 Всё наладится!", "Держись! 💪"],

    "грустно": ["Понимаю... 😔 Может музыку? /music", "Не грусти! 💙"],

}



INTELLIGENCE = {

    "2 + 2": "4",

    "150 + 150": "300",

    "10 * 10": "100",

    "путин": "Владимир Путин - президент России с 2012 года.",

    "кто ты": "Я Cho Второй - твой AI-помощник! 😊",

    "что умеешь": "Умею:\n🎵 /music - музыка\n /video - видео\n🖼️ /img - картинки\n📚 /wiki - информация",

}



CONVERSATION = [

    "Интересно! 😊",

    "Понимаю! 💭",

    "Да, бывает! 😄",

    "Круто! 🔥",

    "Хм... ",

    "Согласен! 👍",

]



def is_family(username):

    """Проверяет является ли пользователь семьёй"""
    if not username:

        return False

    return username.lower() in CREATORS



def is_insult(text):

    """Проверяет есть ли в сообщении оскорбление или мат"""

    text = text.lower()

    for insult in INSULTS:

        if insult in text:

            return True

    return False



def get_response(text, username):

    text_lower = text.lower().strip()

    

    # ЕСЛИ ОСКОРБЛЕНИЕ И НЕ СЕМЬЯ - ЖЁСТКО МАТЕРИМСЯ

    if is_insult(text) and not is_family(username):

        # 70% шанс мата, 30% шанс роаста

        if random.random() < 0.7:

            return random.choice(SWEAR_RESPONSES)

        else:

            return random.choice(ROAST_RESPONSES)

    

    # СНАЧАЛА ИНТЕЛЛЕКТ

    for question, answer in INTELLIGENCE.items():
        if question in text_lower:

            return answer

    

    # ПОТОМ ЭМОЦИИ

    for emotion, responses in EMOTIONAL_RESPONSES.items():

        if emotion in text_lower:

            return random.choice(responses)

    

    # СЛУЧАЙНАЯ ФРАЗА

    return random.choice(CONVERSATION)



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

    username = message.from_user.username

    if is_family(username):

        role = CREATORS.get(username.lower(), "")

        await message.answer(f"Привет, {role}! 😊❤️")

    else:

        await message.answer("Привет! Я Cho Второй! 😊")



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

    username = message.from_user.username

    response = get_response(message.text, username)

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

    print(f"DEBUG: Family members: {list(CREATORS.keys())}")

    t = threading.Thread(target=start_web, daemon=True)

    t.start()

    asyncio.run(polling_with_restart())
