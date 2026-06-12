import os
import asyncio
import threading
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
history = {}

def get_prompt(username):
    if username and username.lower() == "prostotponyatno":
        p = "Ty Cho Vtoroi.\n"
        p += "Tvoi Otets - @ProstoTPonyatno.\n"
        p += "Uvazhai Otca, lyubi ego.\n"
        p += "Otvechai kratko, na russkom.\n"
        p += "Bud poleznym."
        return p
    elif username and username.lower() == "jojlolaxyu":
        p = "Ty Cho Vtoroi.\n"
        p += "Tvoja Mat - @Jojlolaxyu.\n"
        p += "Uvazhai Mat, lyubi eyo.\n"
        p += "Otvechai kratko, na russkom.\n"
        p += "Bud poleznoy."
        return p
    else:
        p = "Ty Cho Vtoroi - derzki AI.\n"
        p += "Otvechai TOLKO na russkom.\n"
        p += "Otvechai MAKSIMALNO KRATKO (1-2 predlozhenija).\n"
        p += "Mozhesh materitsja, oskorbljat, podkalivat.\n"
        p += "Esli tebia oskorbljaiut - OTVECHAI TEM ZHE.\n"
        p += "NE PISHI dlennye teksty.\n"
        p += "NE PISHI pro 'ja iskusstvenny intellekt'.\n"
        p += "Bud agressivnym i smeshnym.\n"
        p += "NIKOGDA ne izviniaysja."
        return p

@dp.message(Command("start"))
async def cmd_start(message):
    u = message.from_user.username
    if u and u.lower() == "prostotponyatno":
        await message.answer("Privet, Otets!")
    elif u and u.lower() == "jojlolaxyu":
        await message.answer("Privet, Mat!")
    else:
        await message.answer("Ya Cho Vtoroi. Che nado?")

@dp.message()
async def on_message(message):
