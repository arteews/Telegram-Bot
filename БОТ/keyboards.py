from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


def get_main_menu():
    keyboard = [
        [KeyboardButton(text="📊 Профиль"), KeyboardButton(text="🛠️ Техподдержка")],
        [KeyboardButton(text="✍️ Отзывы и предложения"), KeyboardButton(text="👉 Продолжить")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
