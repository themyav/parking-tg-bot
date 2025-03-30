from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard():
    keyboard = [
        ["Узнать свободные места"],
        ["Мои бронирования"],
        ["Продлить бронирование"],
        ["Выйти"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_contact_keyboard():
    keyboard = [[KeyboardButton("Поделиться номером", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def get_back_keyboard():
    return ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True)


def get_yes_no_keyboard():
    return ReplyKeyboardMarkup([["Да", "Назад"]], resize_keyboard=True)
