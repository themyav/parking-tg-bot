from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

import states
from states import State
from keyboards import get_main_menu_keyboard, get_back_keyboard
from api_client import APIClient


class ProlongationHandler:
    @staticmethod
    async def handle_prolong_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print('Handle prolog')
        bookings = await APIClient.get_bookings_for_user_id(context.user_data['user']['id'])
        if not bookings:
            await update.message.reply_text(
                "У вас нет активных бронирований для продления.",
                reply_markup=get_main_menu_keyboard()
            )
            return states.State.SELECT_ACTION.value
        print('Has booking')

        keyboard = [[f"{i + 1}. {b['booking_id']}"] for i, b in enumerate(bookings)]
        keyboard.append(["Назад"])
        context.user_data['bookings'] = bookings

        await update.message.reply_text(
            "Выберите бронирование для продления:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return states.State.SELECT_BOOKING_TO_PROLONG.value

    @staticmethod
    async def handle_booking_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Назад":
            await update.message.reply_text(
                "Выберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
            return states.State.SELECT_ACTION.value

        try:
            booking_num = int(text.split('.')[0]) - 1
            bookings = context.user_data['bookings']

            if booking_num < 0 or booking_num >= len(bookings):
                raise ValueError

            context.user_data['selected_booking'] = bookings[booking_num]

            await update.message.reply_text(
                f"Введите новую дату и время окончания для бронирования {bookings[booking_num]['booking_id']} (текущая: {bookings[booking_num]['end_time']}) в формате ДД.ММ.ГГГГ ЧЧ:ММ",
                reply_markup=get_back_keyboard()
            )
            return states.State.PROLONG_BOOKING.value

        except (ValueError, IndexError):
            keyboard = [[f"{i + 1}. {b['booking_id']}"] for i, b in enumerate(context.user_data['bookings'])]
            keyboard.append(["Назад"])

            await update.message.reply_text(
                "Пожалуйста, выберите бронирование из списка:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
            return states.State.SELECT_BOOKING_TO_PROLONG.value

    @staticmethod
    async def handle_new_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Назад":
            await update.message.reply_text(
                "Выберите бронирование для продления:",
                reply_markup=ReplyKeyboardMarkup(
                    [[f"{i + 1}. {b['booking_id']}"] for i, b in enumerate(context.user_data['bookings'])] + [
                        ["Назад"]],
                    resize_keyboard=True)
            )
            return states.State.SELECT_BOOKING_TO_PROLONG.value

        try:
            date_str, time_str = text.split()
            new_end_time = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            booking = context.user_data['selected_booking']

            current_end = datetime.strptime(booking['end_time'], "%Y-%m-%dT%H:%M")
            if new_end_time <= current_end:
                await update.message.reply_text(
                    "Новая дата окончания должна быть позже текущей. Пожалуйста, введите корректную дату:"
                )
                return states.State.PROLONG_BOOKING.value

            status_code = await APIClient.prolongate_booking(booking['booking_id'], new_end_time.isoformat())

            if status_code == 200:
                await update.message.reply_text(
                    f"Бронирование {booking['booking_id']} успешно продлено до {new_end_time}!",
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                await update.message.reply_text(
                    "Произошла ошибка при продлении бронирования. Пожалуйста, попробуйте еще раз.",
                    reply_markup=get_main_menu_keyboard()
                )

            return states.State.SELECT_ACTION.value

        except ValueError:
            await update.message.reply_text(
                "Неправильный формат даты. Пожалуйста, введите в формате ДД.ММ.ГГГГ ЧЧ:ММ\nНапример: 05.12.2023 18:00"
            )
            return states.State.PROLONG_BOOKING.value
