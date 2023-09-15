from aiogram import Bot, Dispatcher, types, html, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, WebAppInfo, WebAppData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import asyncio
import os
import logging

TOKEN = '6191110636:AAEisNjXvHHNyiGCpRE6gRfGaQTN2nV8oK4'
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.DEBUG)


@dp.message(Command("start"))
async def start(message: Message):
    message_text = '1234'
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(
        text="Web",
        web_app=WebAppInfo(url='https://geodeziy.github.io/W-0723/templates/index.html'))
    )
    await message.answer(message_text, parse_mode="HTML", reply_markup=builder.as_markup())

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())