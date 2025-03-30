from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import State
from keyboards import get_main_menu_keyboard, get_contact_keyboard
from api_client import APIClient


class ContactHandler:
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Добро пожаловать в бот управления парковкой! Пожалуйста, поделитесь вашим номером телефона для идентификации.",
            reply_markup=get_contact_keyboard()
        )

    @staticmethod
    async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
        contact = update.message.contact
        if contact:
            phone_number = contact.phone_number
            context.user_data['phone'] = phone_number

            user_data = await APIClient.get_user_by_phone_number(phone_number)
            context.user_data['user'] = user_data

            await update.message.reply_text(
                f"Добро пожаловать, {user_data['id']}!",
                reply_markup=get_main_menu_keyboard()
            )
            return State.SELECT_ACTION.value  # Make sure to return the value
        return ConversationHandler.END
