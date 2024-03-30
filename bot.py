from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, WebAppInfo, WebAppData, MenuButtonWebApp, InlineKeyboardMarkup, InlineKeyboardButton
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
            cursor = await db.execute("SELECT COUNT(*) FROM favourites WHERE user_id = ? AND string_id = ?",
                                      (message.from_user.id, m[3:]))
            row_count = await cursor.fetchone()
            if row_count[0] == 0:
                await db.execute("INSERT OR IGNORE INTO favourites (user_id, string_id) VALUES (?, ?)",
                                 (message.from_user.id, m[3:]))
                await db.commit()
            else:
                pass
                # await message.answer('Такая строка уже существует')
    # await message.answer(message.web_app_data.data)
    await message.answer('Сохранение произошло успешно.')


async def get_values_by_user_id(user_id):
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
async def user_list(message: Message):
    result = await get_values_by_user_id(message.from_user.id)
    if result:
        await message.answer(str(result))
    else:
        await message.answer('None')

# Команда принимает десятичные числа через пробел или одно число.
# Если первый аргумент команды это 16,
# то все числа принимаются в шестнадцатеричной системе счисления, начинающееся на '0x'.
@dp.message(Command('u'))
async def u(message: Message, command: CommandObject):
    try:
        c = command.args.split()
        if c[0] == '16':
            n = list(map(lambda x: int(x, 16), c))
        else:
            n = list(map(lambda x: int(x), c))
        # print(n)
        if len(n) == 1:
            if n == 'NoneType':
                await message.answer('Значение не передано.')
            elif n in range(0, 33):
                await message.answer(
                    'Первые 32 символа Unicode представляют собой '
                    'управляющие символы, пробелы, символы со специальным значением. '
                    'В Telegram нельзя отправить пустое сообщение.')
            else:
                await message.answer(chr(n[0]))
        else:
            s = ''
            for i in n:
                s += chr(i)
            await message.answer(s)

    except ValueError as e:
        await message.answer(f'Значение вне диапазона Unicode [0; 1114111].')
    except AttributeError:
        await message.answer('В вашей команде должно содержаться значение.')


async def main():
    dp.include_router(start.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
