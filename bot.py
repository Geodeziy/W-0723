from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, WebAppInfo, WebAppData,  MenuButtonWebApp, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import asyncio
import os
import logging
from settings import TOKEN
from handlers import start
import aiosqlite

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
    m = message.web_app_data.data
    if m.startswith('id_'):
        async with aiosqlite.connect("data.db") as db:
            await db.execute("INSERT OR IGNORE INTO favourites (user_id, string_id) VALUES (?, ?)", (message.from_user.id, m[3:]))
            await db.commit()
    await message.answer(message.web_app_data.data)


async def get_string_values_by_user_id(user_id):
    async with aiosqlite.connect("data.db") as db:
        cursor = await db.execute('''
                    SELECT string_id
                    FROM favourites
                    WHERE user_id = ?
                ''', (user_id,))
        string_ids = await cursor.fetchall()

        result = []
        for string_id in string_ids:
            cursor = await db.execute('''
                        SELECT string
                        FROM id
                        WHERE id = ?
                    ''', (string_id[0],))
            string_value = await cursor.fetchone()
            if string_value:
                result.append(string_value[0])

        return result


@dp.message(Command('list'))
async def command_webview(message: Message):
    result = await get_string_values_by_user_id(message.from_user.id)
    if result:
        await message.answer(str(result))
    else:
        await message.answer('None')

async def main():
    dp.include_router(start.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
