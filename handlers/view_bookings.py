from telegram import Update
from telegram.ext import ContextTypes
from states import State
from keyboards import get_main_menu_keyboard
from api_client import APIClient


class ViewBookingsHandler:
    @staticmethod
    async def handle_view_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        bookings = await APIClient.get_bookings_for_user_id(context.user_data['user']['id'])
        if not bookings:
            await update.message.reply_text(
                "У вас нет активных бронирований.",
                reply_markup=get_main_menu_keyboard()
            )
            return State.SELECT_ACTION.value  # Add .value here

        bookings_text = "\n".join(
            f"{i + 1}. Место {b['booking_id']}: с {b['start_time']} по {b['end_time']}, авто {b['car_number']}"
            for i, b in enumerate(bookings)
        )
        context.user_data['bookings'] = bookings

        await update.message.reply_text(
            f"Ваши бронирования:\n{bookings_text}",
            reply_markup=get_main_menu_keyboard()
        )
        return State.SELECT_ACTION.value  # Add .value here
