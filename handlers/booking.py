from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

import states
from states import State
from keyboards import get_back_keyboard, get_yes_no_keyboard, get_main_menu_keyboard
from api_client import APIClient


class BookingHandler:
    @staticmethod
    async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Узнать свободные места":
            await update.message.reply_text(
                "Введите дату и время начала бронирования в формате ДД.ММ.ГГГГ ЧЧ:ММ\nНапример: 01.12.2023 10:00",
                reply_markup=get_back_keyboard()
            )
            return State.GET_START_DATE.value  # Add .value here

        return State.SELECT_ACTION.value  # Add .value here

    @staticmethod
    async def handle_start_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Назад":
            await update.message.reply_text(
                "Выберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
            return states.State.SELECT_ACTION.value

        try:
            date_str, time_str = text.split()
            start_time = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            context.user_data['start_time'] = start_time.isoformat()

            await update.message.reply_text(
                "Введите дату и время окончания бронирования в формате ДД.ММ.ГГГГ ЧЧ:ММ\nНапример: 05.12.2023 18:00",
                reply_markup=get_back_keyboard()
            )
            return states.State.GET_END_DATE.value

        except ValueError:
            await update.message.reply_text(
                "Неправильный формат даты. Пожалуйста, введите в формате ДД.ММ.ГГГГ ЧЧ:ММ\nНапример: 01.12.2023 10:00"
            )
            return states.State.GET_START_DATE.value

    @staticmethod
    async def handle_end_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Назад":
            await update.message.reply_text(
                "Введите дату и время начала бронирования:",
                reply_markup=get_back_keyboard()
            )
            return states.State.GET_START_DATE.value

        try:
            date_str, time_str = text.split()
            end_time = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            start_time = datetime.fromisoformat(context.user_data['start_time'])

            if end_time <= start_time:
                await update.message.reply_text(
                    "Время окончания должно быть позже времени начала. Пожалуйста, введите корректное время:"
                )
                return states.State.GET_END_DATE.value

            context.user_data['end_time'] = end_time.isoformat()

            parkings = await APIClient.get_available_parkings_for_id(
                context.user_data['user']['id'],
                context.user_data['start_time'],
                context.user_data['end_time']
            )

            if not parkings:
                await update.message.reply_text(
                    "Нет доступных мест на выбранные даты.",
                    reply_markup=get_main_menu_keyboard()
                )
                return states.State.SELECT_ACTION.value

            context.user_data['parkings'] = parkings
            keyboard = [[p['id']] for p in parkings]
            keyboard.append(["Назад"])

            parkings_text = "\n".join(
                f"{p['id']} - {p['cost_per_day']} руб/день, {p['cost_per_hour']} руб/час"
                for p in parkings
            )

            await update.message.reply_text(
                f"Доступные места:\n{parkings_text}\n\nВыберите место:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
            return states.State.SELECT_PARKING.value

        except ValueError:
            await update.message.reply_text(
                "Неправильный формат даты. Пожалуйста, введите в формате ДД.ММ.ГГГГ ЧЧ:ММ\nНапример: 05.12.2023 18:00"
            )
            return states.State.GET_END_DATE.value

    @staticmethod
    async def handle_parking_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Назад":
            await update.message.reply_text(
                "Выберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
            return states.State.SELECT_ACTION.value

        parkings = context.user_data['parkings']
        selected_parking = next((p for p in parkings if p['id'] == text), None)

        if not selected_parking:
            await update.message.reply_text(
                "Пожалуйста, выберите место из списка:",
                reply_markup=ReplyKeyboardMarkup([[p['id'] for p in parkings] + ["Назад"]], resize_keyboard=True)
            )
            return states.State.SELECT_PARKING.value

        context.user_data['selected_parking'] = selected_parking

        await update.message.reply_text(
            f"Вы выбрали место {selected_parking['id']}. Забронировать его с {context.user_data['start_time']} по {context.user_data['end_time']}?",
            reply_markup=get_yes_no_keyboard()
        )
        return states.State.CONFIRM_BOOKING.value

    @staticmethod
    async def handle_booking_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Назад":
            parkings = context.user_data['parkings']
            keyboard = [[p['id']] for p in parkings]
            keyboard.append(["Назад"])

            await update.message.reply_text(
                "Выберите место:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
            return states.State.SELECT_PARKING.value

        if text == "Да":
            await update.message.reply_text(
                "Введите госномер вашего автомобиля:",
                reply_markup=get_back_keyboard()
            )
            return states.State.INPUT_CAR_NUMBER.value

        return states.State.CONFIRM_BOOKING.value

    @staticmethod
    async def handle_car_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == "Назад":
            await update.message.reply_text(
                f"Вы выбрали место {context.user_data['selected_parking']['id']}. Забронировать его?",
                reply_markup=get_yes_no_keyboard()
            )
            return states.State.CONFIRM_BOOKING.value

        context.user_data['car_number'] = text

        status_code = await APIClient.book_place(
            context.user_data['user']['id'],
            context.user_data['selected_parking']['id'],
            context.user_data['start_time'],
            context.user_data['end_time'],
            context.user_data['car_number']
        )

        if status_code == 200:
            await update.message.reply_text(
                f"Место {context.user_data['selected_parking']['id']} успешно забронировано!",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "Произошла ошибка при бронировании. Пожалуйста, попробуйте еще раз.",
                reply_markup=get_main_menu_keyboard()
            )

        return states.State.SELECT_ACTION.value
