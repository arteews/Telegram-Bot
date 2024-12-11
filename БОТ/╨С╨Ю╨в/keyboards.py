from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu():
    keyboard = [
        [KeyboardButton(text="📊 Профиль"), KeyboardButton(text="🛠️ Техподдержка")],
        [KeyboardButton(text="✍️ Отзывы и предложения"), KeyboardButton(text="✉️ Рассылки")],
        [KeyboardButton(text="👉 Продолжить")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)



def get_inline_menu():
    # Инлайн-клавиатура в стиле с предыдущим примером, но с текстом Культура, Еда, Развлечения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Культура 🖼️", callback_data="culture")],
        [InlineKeyboardButton(text="Еда 🍰", callback_data="food")],
        [InlineKeyboardButton(text="Развлечения 🎉", callback_data="entertainment")]
    ])
    return keyboard


def get_inlines_menu():
    # Инлайн-клавиатура в стиле с предыдущим примером, но с текстом Культура, Еда, Развлечения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Музеи 🏛️", callback_data="museums")],
        [InlineKeyboardButton(text="Памятники 🗽", callback_data="monuments")],
        [InlineKeyboardButton(text="Назад", callback_data="baksii")]
    ])
    return keyboard



def get_inliness_menu():
    # Инлайн-клавиатура в стиле с предыдущим примером, но с текстом Культура, Еда, Развлечения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню", callback_data="munesd")]
      ])
    return keyboard