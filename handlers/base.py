from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_menu_keyboard


class BaseHandler:
    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз.",
            reply_markup=get_main_menu_keyboard()
        )
