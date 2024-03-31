from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, WebAppInfo, WebAppData, MenuButtonWebApp, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums import ParseMode
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
        "Нажмите на кнопку чтобы открыть веб-просмотр.",
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
        await message.answer('Ваш список:\n' + '\n'.join(f"{index + 1}. {item}" for index, item in enumerate(result))
                             + '.')
    else:
        await message.answer('None')


@dp.message(Command('delete'))
async def delete_item(message: Message, command: CommandObject):
    try:
        if command.args is None:
            await message.answer('Не передано значение.')
        else:
            user_id = message.from_user.id
            element = int(command.args[0])
            async with aiosqlite.connect('data.db') as db:
                async with db.execute(f"SELECT * FROM favourites WHERE user_id = ? LIMIT 1 OFFSET ?",
                                      (user_id, element - 1)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        await db.execute("DELETE FROM favourites WHERE user_id = ? AND id = ?", (user_id, row[0]))
                        await db.commit()
                        await message.answer(f"Успешно удалено.")
                    else:
                        await message.answer(f"Строка с номером {element} не найдена.")
    except aiosqlite.Error as e:
        await message.answer("Ошибка при работе с базой данных:", e)


# Команда принимает десятичные числа через пробел или одно число и декодирует их в символы Unicode.
@dp.message(Command('decode'))
async def decode(message: Message, command: CommandObject):
    try:
        if command.args is None:
            await message.answer('Не переданы число или числа.')
        else:
            c = command.args.split()
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

    except ValueError:
        await message.answer(f'Значение вне диапазона Unicode [0; 1114111].')
    except AttributeError:
        await message.answer('В вашей команде должно содержаться значение.')


# Команда принимает шестнадцатеричные числа через пробел или одно число и декодирует их в символы Unicode.
@dp.message(Command('decode16'))
async def decode16(message: Message, command: CommandObject):
    try:
        if command.args is None:
            await message.answer('Не переданы число или числа.')
        else:
            c = command.args.split()
            n = list(map(lambda x: int(x, 16), c))
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

    except ValueError:
        await message.answer(f'Значение вне диапазона Unicode [0; 1114111].')
    except AttributeError:
        await message.answer('В вашей команде должно содержаться значение.')


# Функция кодирует переданную строку.
@dp.message(Command('encode'))
async def encode(message: Message, command: CommandObject):
    try:
        if command.args is None:
            await message.answer('Не передана строка.')
        else:
            symbols = list(command.args)
            if len(symbols) == 1:
                await message.answer(str(ord(symbols[0])))
            else:
                s = ''
                for i in symbols:
                    s += str(ord(i)) + ' '
                await message.answer(s)

    except Exception as e:
        await message.answer(e)


# Функция кодирует переданную строку в шестнадцатеричный формат.
@dp.message(Command('encode16'))
async def encode16(message: Message, command: CommandObject):
    try:
        if command.args is None:
            await message.answer('Не передана строка.')
        else:
            symbols = list(command.args)
            if len(symbols) == 1:
                await message.answer(str(hex(ord(symbols[0]))))
            else:
                s = ''
                for i in symbols:
                    s += str(hex(ord(i))) + ' '
                await message.answer(s)

    except Exception as e:
        await message.answer(e)


@dp.message(Command('help'))
async def help_function(message: Message):
    await message.answer('Список доступных команд:\n'
                         '> /help - отправляет это сообщение.\n'
                         '> /webview - отправляет сообщение с кнопкой для открытия веб-справочника.\n'
                         '> /list - отправляет сообщение с сохранённым списком названий статей из веб-справочника.\n'
                         '> /delete <em>номер из списка</em> - '
                         'удаляет из вашего списка строку под соответствующим номером.\n'
                         '> /decode <em>десятичное число или числа</em> - возвращает строку из символов Unicode, '
                         'чьи номера соответствуют переданным.\n'
                         '> /decode16 <em>шестнадцатеричное число или числа</em> - '
                         'возвращает строку из символов Unicode, '
                         'чьи номера соответствуют переданным.\n'
                         '> /encode <em>строка</em> - '
                         'кодирует строку в десятичные номера символов Unicode.\n'
                         '> /encode16 <em>строка</em> - '
                         'кодирует строку в шестнадцатеричные номера символов Unicode.\n', parse_mode=ParseMode.HTML)


async def main():
    dp.include_router(start.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
