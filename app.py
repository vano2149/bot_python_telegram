"""
My bot!
"""
import os
import asyncio
import logging
from typing import List, Tuple, cast

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ =(0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB {TG_VER}. To view the "
        f"{TG_VER} version of this example. "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    InvalidCallbackData,
    PicklePersistence,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a message with 5 inline buttons attached.
    """
    chat_id = update.message.chat_id
    await asyncio.sleep(5)
    await context.bot.send_chat_action(chat_id, action=constants.ChatAction.TYPING)
    await context.bot.send_message(
                            chat_id, 
                            text=
                            f"Hello, I'm SHOKOPAL Bot. Then I can halp you!\n"
                            f"Wrigth the /help command to get my command!")
    number_list: List[int] = []
    await update.message.reply_text("Please choose:", reply_markup=build_keyboard(number_list))

async def help_command(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    """
    Display info on how to use the bot!
    """
    await update.message.reply_text(
        "Use /start to testthis bot. Use /clear to clear the stored data so that you can see "
        "what happenes, if the button data is not available. ")

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    await context.bot.send_message(chat_id, text=f"Your chat_id {chat_id}")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears the callback data cache"""
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    await update.effective_message.reply_text("All clear!")

async def build_keyboard(current_list: List[int]) -> InlineKeyboardMarkup:
    """
    Helped function to build the next inline keyboard.
    """
    return InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(str(i), callback_data=(i, current_list)) for i in range(1,6)]
    )

async def list_button(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    """
    Parses the CallbackQuery and update the message text.
    """
    query = update.callback_query
    await query.answer()

    number, number_list = cast(Tuple[int, List[int]], query.data)
    number_list.append(number)

    await query.edit_message_text(
        text=f"So far you've selected {number_list}. Choose the next item:",
        reply_markup=build_keyboard(number_list),
    )
    context.drop_callback_data(query)

async def handle_invalid_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Informs the user that the button is no longer available."""
    await update.callback_query.answer()
    await update.effective_message.edit_text(
        "Sorry, I could not process this button click 😕 Please send /start to get a new keyboard."
    )


def main() -> None:
    """
    Run the bot.
    """

    persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")

    application = (
        Application.builder()
        .token(os.environ.get("TOKEN"))
        .persistence(persistence)
        .arbitrary_callback_data(True)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(CommandHandler("chat_id", chat_id))


    application.add_handler(
        CallbackQueryHandler(handle_invalid_button, pattern=InvalidCallbackData)
    )
    application.add_handler(CallbackQueryHandler(list_button))


    application.run_polling()


if __name__ == '__main__':
    main()