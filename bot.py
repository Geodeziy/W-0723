from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, WebAppInfo, WebAppData,  MenuButtonWebApp, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import asyncio
import os
import logging
from settings import TOKEN
from handlers import start

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.DEBUG)



@dp.message(Command("webview"))
async def command_webview(message: Message):
    await message.answer(
        "Нажмите на кнопку чтобы открыть веб-просмотр",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Web", web_app=WebAppInfo(url="https://geodeziy.github.io/W-0723/templates/index.html")
                    )
                ]
            ]
        ),
    )


# @dp.message(lambda x: x.web_app_data != None)
@dp.message(F.web_app_data)
async def appdata(message: Message):
    await message.answer(message.web_app_data.data)


async def main():
    dp.include_router(start.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
