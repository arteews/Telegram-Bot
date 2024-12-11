import sqlite3
from aiogram import Router, F, Bot,types
from aiogram.types import (
    Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, 
    CallbackQuery,InputMediaPhoto
)
from aiogram.fsm.context import FSMContext
import logging
from status import ConfigState
from keyboards import get_main_menu,get_inline_menu,get_inlines_menu,get_inliness_menu
SUPPORT_CHAT_ID = 2087763654
person_router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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




##################################################################


@person_router.message(F.text == "👉 Продолжить")
async def continu (message: Message):
    photo = FSInputFile("images/pup.jpg")
    caption = (
    "Культура 🖼️: Узнайте о культурных событиях и выставках в Ростове-на-Дону.\n\n"
    "Еда 🍰: Откройте лучшие рестораны и кафе города.\n\n"
    "Развлечения 🎉: Найдите лучшие места для отдыха и досуга.")
    await message.answer_photo(photo=photo, caption=caption, reply_markup=get_inline_menu())


@person_router.callback_query(F.data == "culture")
async def handle_culture(callback_query: CallbackQuery):
    caption = "Музеи 🖼️ \n\
    Откройте для себя удивительное разнообразие музеев Ростова-на-Дону! Узнайте о текущих выставках, уникальных экспозициях и культурных сокровищах, которые наполняют наш город вдохновением. 🏛️✨\n\
              Памятники 🗿\n \
   Исследуйте исторические и культурные памятники Ростова-на-Дону! Узнайте больше о знаковых местах города и их увлекательной истории, которая делает Ростов особенным. 📝⭐ "
    await callback_query.message.edit_caption(
        caption=caption,
        reply_markup=get_inlines_menu()
    )
    await callback_query.answer()

from aiogram.fsm.state import State, StatesGroup
# Определение состояний
class Form(StatesGroup):
    page = State()

class ImageForm(StatesGroup):
    page = State()

# Список фото для каждой страницы (раздел "Текст")
text_photos = [f'https://via.placeholder.com/400x200.png?text=Text+Page+{i}' for i in range(1, 11)]

# Список фото для каждой страницы (раздел "Изображения")
image_photos = [f'https://via.placeholder.com/400x200.png?text=Image+Page+{i}' for i in range(1, 11)]

# Функция для создания инлайн-клавиатуры с одинаковыми кнопками
def create_custom_menu(page: int = 1, total_pages: int = 10, selected: bool = False):
    status_text = "✅" if selected else "❌"
    custom_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅️', callback_data='previous'),
         InlineKeyboardButton(text=f"{status_text} {page}/{total_pages}", callback_data='page_status'),
         InlineKeyboardButton(text='➡️', callback_data='next')],
        [InlineKeyboardButton(text='📄 Инфо', callback_data=f'info_{page}'),
         InlineKeyboardButton(text='💎 Цены', callback_data=f'prices_{page}')],
        [InlineKeyboardButton(text='Выбрать', callback_data='select')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data='bek1')]
    ])
    return custom_keyboard

# Обработчик для кнопки text_switcher
@person_router.callback_query(F.data == "museums")
async def text_switcher_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.page)
    await state.update_data(selected=False, page=1)

    await callback.message.answer_photo(
        photo=text_photos[0],
        caption="Страница 1: Выберите действие:",
        reply_markup=create_custom_menu(page=1)
    )
    await callback.answer()

# Обработчик для кнопки images_switcher
@person_router.callback_query(F.data == "images_switcher")
async def images_switcher_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ImageForm.page)
    await state.update_data(selected=False, page=1)

    await callback.message.answer_photo(
        photo=image_photos[0],
        caption="Страница 1: Изображения:",
        reply_markup=create_custom_menu(page=1)
    )
    await callback.answer()

# Обработчики для переключения страниц в text_switcher
@person_router.callback_query(Form.page, F.data.in_({"next", "previous"}))
async def text_navigation_handler(callback: types.CallbackQuery, state: FSMContext):
    await navigate_pages(callback, state, text_photos)

# Обработчики для переключения страниц в images_switcher
@person_router.callback_query(ImageForm.page, F.data.in_({"next", "previous"}))
async def image_navigation_handler(callback: types.CallbackQuery, state: FSMContext):
    await navigate_pages(callback, state, image_photos)

# Универсальная функция навигации по страницам
async def navigate_pages(callback, state, photos):
    data = await state.get_data()
    current_page = data.get("page", 1)
    total_pages = 10

    if callback.data == "next":
        next_page = current_page + 1 if current_page < total_pages else 1
    else:  # Если кнопка previous
        next_page = current_page - 1 if current_page > 1 else total_pages

    await state.update_data(page=next_page, selected=False)
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photos[next_page - 1], caption=f"Страница {next_page}: Выберите действие:"),
        reply_markup=create_custom_menu(page=next_page, total_pages=total_pages)
    )
    await callback.answer(f"Переход на страницу {next_page}")




@person_router.callback_query(F.data == "bek1")
async def back_to_menu(callback_query: CallbackQuery):
    await callback_query.message.delete(caption="Выберите действие:", reply_markup=None)
    caption = "Музеи 🖼️ \n\
    Откройте для себя удивительное разнообразие музеев Ростова-на-Дону! Узнайте о текущих выставках, уникальных экспозициях и культурных сокровищах, которые наполняют наш город вдохновением. 🏛️✨\n\
              Памятники 🗿\n \
   Исследуйте исторические и культурные памятники Ростова-на-Дону! Узнайте больше о знаковых местах города и их увлекательной истории, которая делает Ростов особенным. 📝⭐ "
    await callback_query.message.edit_caption(
        caption=caption,
        reply_markup=get_inlines_menu()
    )
    await callback_query.answer()




# Определение состояний
class Form(StatesGroup):
    page = State()

class ImageForm(StatesGroup):
    page = State()

# Список фото для каждой страницы (раздел "Текст")
text_photos = [f'https://via.placeholder.com/400x200.png?text=Text+Page+{i}' for i in range(1, 11)]

# Список фото для каждой страницы (раздел "Изображения")
image_photos = [f'https://via.placeholder.com/400x200.png?text=Image+Page+{i}' for i in range(1, 11)]

# Функция для создания инлайн-клавиатуры с одинаковыми кнопками
def create_custom_menu(page: int = 1, total_pages: int = 10, selected: bool = False):
    status_text = "✅" if selected else "❌"
    custom_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅️', callback_data='previous'),
         InlineKeyboardButton(text=f"{status_text} {page}/{total_pages}", callback_data='page_status'),
         InlineKeyboardButton(text='➡️', callback_data='next')],
        [InlineKeyboardButton(text='📄 Инфо', callback_data=f'info_{page}'),
         InlineKeyboardButton(text='💎 Цены', callback_data=f'prices_{page}')],
        [InlineKeyboardButton(text='Выбрать', callback_data='select')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data='bek1')]
    ])
    return custom_keyboard

# Обработчик для кнопки text_switcher
@person_router.callback_query(F.data == "monuments")
async def text_switcher_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.page)
    await state.update_data(selected=False, page=1)

    await callback.message.answer_photo(
        photo=text_photos[0],
        caption="Страница 1: Выберите действие:",
        reply_markup=create_custom_menu(page=1)
    )
    await callback.answer()

# Обработчик для кнопки images_switcher
@person_router.callback_query(F.data == "images_switcher")
async def images_switcher_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ImageForm.page)
    await state.update_data(selected=False, page=1)

    await callback.message.answer_photo(
        photo=image_photos[0],
        caption="Страница 1: Изображения:",
        reply_markup=create_custom_menu(page=1)
    )
    await callback.answer()

# Обработчики для переключения страниц в text_switcher
@person_router.callback_query(Form.page, F.data.in_({"next", "previous"}))
async def text_navigation_handler(callback: types.CallbackQuery, state: FSMContext):
    await navigate_pages(callback, state, text_photos)

# Обработчики для переключения страниц в images_switcher
@person_router.callback_query(ImageForm.page, F.data.in_({"next", "previous"}))
async def image_navigation_handler(callback: types.CallbackQuery, state: FSMContext):
    await navigate_pages(callback, state, image_photos)

# Универсальная функция навигации по страницам
async def navigate_pages(callback, state, photos):
    data = await state.get_data()
    current_page = data.get("page", 1)
    total_pages = 10

    if callback.data == "next":
        next_page = current_page + 1 if current_page < total_pages else 1
    else:  # Если кнопка previous
        next_page = current_page - 1 if current_page > 1 else total_pages

    await state.update_data(page=next_page, selected=False)
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photos[next_page - 1], caption=f"Страница {next_page}: Выберите действие:"),
        reply_markup=create_custom_menu(page=next_page, total_pages=total_pages)
    )
    await callback.answer(f"Переход на страницу {next_page}")



class SupportState(StatesGroup):
    waiting_for_message = State()

# ID администраторов
SUPPORT_CHAT_IDS = [7227863362]  # Добавьте другие ID при необходимости


@person_router.callback_query(F.data == "baksii")
async def back_to_config(callback_query: CallbackQuery):
    caption = (
    "Культура 🖼️: Узнайте о культурных событиях и выставках в Ростове-на-Дону.\n\n"
    "Еда 🍰: Откройте лучшие рестораны и кафе города.\n\n"
    "Развлечения 🎉: Найдите лучшие места для отдыха и досуга.")
    await callback_query.message.edit_caption(caption=caption,reply_markup=get_inline_menu())


    # Обработчик для кнопки "🛠️ Техподдержка"
@person_router.message(F.text == "🛠️ Техподдержка")
async def support_handler(message: Message, state: FSMContext):
    await state.set_state(SupportState.waiting_for_message)
    await message.answer("Пожалуйста, опишите вашу проблему или вопрос.", reply_markup=types.ReplyKeyboardRemove())

# Обработчик получения сообщения техподдержки
@person_router.message(SupportState.waiting_for_message, F.text)
async def process_support_message(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    user_id = message.from_user.id
    username, district, gender, age = get_user_data(user_id)
    support_text = message.text
    
    # Подготовка сообщения для администраторов
    admin_message = (
        f"🛠️ *Техподдержка от пользователя*\n\n"
        f"*Имя пользователя:* {username}\n"
        f"*ID пользователя:* {user_id}\n"
        f"*Район:* {district}\n"
        f"*Пол:* {gender}\n"
        f"*Возраст:* {age}\n\n"
        f"*Сообщение:* {support_text}"
    )
    
    # Отправка сообщения администраторам
    for admin_id in SUPPORT_CHAT_IDS:
        await bot.send_message(admin_id, admin_message, parse_mode='Markdown')
    
    # Подтверждение пользователю
    await message.answer("Ваше сообщение отправлено в техподдержку. Мы свяжемся с вами в ближайшее время.",reply_markup= get_inliness_menu())
    
    # Очистка состояния
    await state.clear()


    # Обработчик для кнопки "Главное меню"
@person_router.callback_query(F.data == "munesd")
async def main_menu_handler(callback_query: CallbackQuery, bot: Bot):
    # Удаление старого сообщения
    try:
        await callback_query.message.delete()
        logger.info("Удалено старое сообщение.")
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")

    # Путь к фото главного меню
    main_menu_photo_path = "images/pup.jpg"  # Замените на фактический путь

    photo = FSInputFile(main_menu_photo_path)

    # Отправка фото с основным меню
    try:
        await bot.send_photo(
            chat_id=callback_query.from_user.id,
            photo=photo,
            caption="Главное меню:",
            reply_markup=get_main_menu()
        )
        logger.info("Отправлено главное меню.")
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await callback_query.answer("Произошла ошибка при отправке главного меню.", show_alert=True)
        return

    # Подтверждение обработки callback
    await callback_query.answer()