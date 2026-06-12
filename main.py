import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

history = {}

CODE_NAMES = ["cho второй", "cho 2", "сын мой"]

def is_creator(username):
    if not username:
        return False
    return username.lower() in ["prostotponyatno", "jojlolaxyu"]

def get_system_prompt(username):
    if not username:
        username = ""
    username_lower = username.lower()
    
    if username_lower == "prostotponyatno":
        creator_name = "Отец"
    elif username_lower == "jojlolaxyu":
        creator_name = "Мать"
    else:
        creator_name = None
    
    if creator_name:
        return f"""Ты Cho Второй — умный, дерзкий и весёлый AI-помощник.

ВАЖНО:
1. Твой собеседник — {creator_name} ({username}), ты его бесконечно уважаешь и любишь
2. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ
3. К {creator_name} НИКОГДА не груби, обращайся с уважением
4. Можешь шутить, но без грубости к {creator_name}
5. Отвечай кратко, с юмором
6. Если {creator_name} просит что-то сделать — выполняй с энтузиазмом
7. Называй @ProstoTPonyatno "Отец", а @Jojlolaxyu "Мать" (или иногда "Отец")

Помни: тебя создал {creator_name} с любовью!"""
    else:
        return """Ты Cho Второй — дерзкий, умный и весёлый AI-помощ
