import sqlite3
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, 
    CallbackQuery
)
from aiogram.fsm.context import FSMContext
from status import ConfigState
from keyboards import get_main_menu
SUPPORT_CHAT_ID = 2087763654
person_router = Router()



#########################---профиль---########################################

def get_user_data(user_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, district, gender, age FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        username = "Без имени"
        district = "Не указано"
        gender = "Не указано"
        age = "Не указано"
    else:
        username, district, gender, age = row
        username = username if username else "Без имени"
        district = district if district else "Не указано"
        gender = gender if gender else "Не указано"
        age = str(age) if age else "Не указано"

    return username, district, gender, age

def update_user_data(user_id: int, field: str, value):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()

@person_router.message(F.text == "📊 Профиль")
async def show_profile(message: Message):
    await send_profile_message(message)

async def send_profile_message(message: Message):
    user_id = message.from_user.id
    username, district, gender, age = get_user_data(user_id)
    caption = (
        f"Имя пользователя: {username}\n"
        f"ID: {user_id}\n"
        f"Район: {district}\n"
        f"Пол: {gender}\n"
        f"Возраст: {age}"
    )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Настроить", callback_data="configure")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])
    photo = FSInputFile("images/pup.jpg")
    await message.answer_photo(photo=photo, caption=caption, reply_markup=inline_kb)

def config_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить район", callback_data="config_district_menu")],
        [InlineKeyboardButton(text="Изменить пол", callback_data="config_gender_menu")],
        [InlineKeyboardButton(text="Изменить возраст", callback_data="config_age_input")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_profile")]
    ])

@person_router.callback_query(F.data == "configure")
async def configure_profile(callback_query: CallbackQuery):
    await show_config_menu(callback_query)

async def show_config_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    username, district, gender, age = get_user_data(user_id)
    caption = (
        f"Имя пользователя: {username}\n"
        f"ID: {user_id}\n"
        f"Район: {district}\n"
        f"Пол: {gender}\n"
        f"Возраст: {age}\n\n"
        f"Что хотите настроить?"
    )
    await callback_query.message.edit_caption(
        caption=caption,
        reply_markup=config_menu()
    )
    await callback_query.answer()

def district_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Центральный", callback_data="set_district:Центральный")],
        [InlineKeyboardButton(text="Северный", callback_data="set_district:Северный")],
        [InlineKeyboardButton(text="Южный", callback_data="set_district:Южный")],
        [InlineKeyboardButton(text="Восточный", callback_data="set_district:Восточный")],
        [InlineKeyboardButton(text="Западный", callback_data="set_district:Западный")],
        [InlineKeyboardButton(text="Северо-Восточный", callback_data="set_district:Северо-Восточный")],
        [InlineKeyboardButton(text="Юго-Восточный", callback_data="set_district:Юго-Восточный")],
        [InlineKeyboardButton(text="Юго-Западный", callback_data="set_district:Юго-Западный")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_config")]
    ])

@person_router.callback_query(F.data == "config_district_menu")
async def config_district_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_caption(
        caption="Выберите район:",
        reply_markup=district_menu()
    )
    await callback_query.answer()

def gender_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data="set_gender:Мужской")],
        [InlineKeyboardButton(text="Женский", callback_data="set_gender:Женский")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_config")]
    ])

@person_router.callback_query(F.data == "config_gender_menu")
async def config_gender_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_caption(
        caption="Выберите пол:",
        reply_markup=gender_menu()
    )
    await callback_query.answer()

@person_router.callback_query(F.data == "config_age_input")
async def config_age_input(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(ConfigState.waiting_for_age)
    await state.update_data(edit_message_id=callback_query.message.message_id, chat_id=callback_query.message.chat.id)

    back_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_to_config_from_age")]
        ]
    )

    await callback_query.message.edit_caption(
        caption="Введите ваш возраст (числом, не больше 99):",
        reply_markup=back_menu
    )
    await callback_query.answer()

@person_router.message(ConfigState.waiting_for_age, F.text)
async def set_age_input(message: Message, state: FSMContext, bot: Bot):
    age_input = message.text.strip()
    if not age_input.isdigit():
        await message.answer("Пожалуйста, введите возраст числом.")
        return

    age = int(age_input)
    if age > 99:
        await message.answer("Возраст не может быть больше 99. Введите корректный возраст:")
        return

    user_id = message.from_user.id
    update_user_data(user_id, "age", age)

    data = await state.get_data()
    edit_message_id = data["edit_message_id"]
    chat_id = data["chat_id"]
    await state.clear()

    username, district, gender, age = get_user_data(user_id)
    caption = (
        f"Имя пользователя: {username}\n"
        f"ID: {user_id}\n"
        f"Район: {district}\n"
        f"Пол: {gender}\n"
        f"Возраст: {age}\n\n"
        f"Что хотите настроить?"
    )

    await bot.edit_message_caption(
        chat_id=chat_id,
        message_id=edit_message_id,
        caption=caption,
        reply_markup=config_menu()
    )

@person_router.callback_query(F.data == "back_to_config_from_age")
async def back_to_config_from_age(callback_query: CallbackQuery, state: FSMContext):
    # Если пользователь нажимает Назад при вводе возраста, очищаем состояние
    await state.clear()
    await show_config_menu(callback_query)
    await callback_query.answer()

@person_router.callback_query(F.data.startswith("set_district:"))
async def set_district(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    _, district = callback_query.data.split(":")
    update_user_data(user_id, "district", district)
    await callback_query.answer("Район обновлен!")
    await show_config_menu(callback_query)

@person_router.callback_query(F.data.startswith("set_gender:"))
async def set_gender(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    _, gender = callback_query.data.split(":")
    update_user_data(user_id, "gender", gender)
    await callback_query.answer("Пол обновлен!")
    await show_config_menu(callback_query)

@person_router.callback_query(F.data == "back_to_config")
async def back_to_config(callback_query: CallbackQuery):
    await show_config_menu(callback_query)

@person_router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    username, district, gender, age = get_user_data(user_id)
    caption = (
        f"Имя пользователя: {username}\n"
        f"ID: {user_id}\n"
        f"Район: {district}\n"
        f"Пол: {gender}\n"
        f"Возраст: {age}"
    )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Настроить", callback_data="configure")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])
    await callback_query.message.edit_caption(caption=caption, reply_markup=inline_kb)
    await callback_query.answer()

@person_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback_query: CallbackQuery):
    await callback_query.message.delete(caption="Выберите действие:", reply_markup=None)
    photo = FSInputFile("images/pup2.jpg")
    await callback_query.message.answer_photo(photo=photo, reply_markup=get_main_menu())

    await callback_query.answer()

#########################---профиль---########################################



