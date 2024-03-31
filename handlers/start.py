from aiogram import Bot, Dispatcher, types, html, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, WebAppInfo, WebAppData,  MenuButtonWebApp, InlineKeyboardMarkup, InlineKeyboardButton
from filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.message(Command("start"))
async def command_start(message: Message, bot: Bot):
    # await bot.set_chat_menu_button(
    #     chat_id=message.chat.id,
    #     menu_button=MenuButtonWebApp(text="Web", web_app=WebAppInfo(url="https://geodeziy.github.io/W-0723/templates/index.html")),
    # )
    await message.answer("""Здравствуйте. Это бот с веб-справочником. Чтобы открыть веб-страницу справочника наберите эту команду /webview и нажмите
     на кнопку под отправленным сообщением. Для дополнительных команд наберите команду /help.""")