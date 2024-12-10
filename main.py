import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import TTLCache

from handlers import (get_private_routers, get_not_private, include_routers, work_router, get_all_routers)
from handlers.ai_handler import ai_router
from database.build import PostgresBuild
from database.model import Base
from utils.nats_connect import connect_to_nats
from storage.nats_storage import NatsStorage
from database.action_data_class import default_properties_set
from middlewares.transfer_middleware import TransferObjectsMiddleware
from middlewares.private_middleware import PrivateMiddleware
from middlewares.op_middlewares import DietOPMiddleware, WorksOPMiddleware, ProfOPMiddleware
from it import client_router as help_router
from client import client_router as diet_router
from dialogs import get_dialogs
from dialogs import work_dialog
from config import BOT_TOKEN


# Инициализация хранилища данных
async def build_storage():
    nc, js = await connect_to_nats(servers=['nats://localhost:4222'])
    storage: NatsStorage = await NatsStorage(nc=nc, js=js).create_storage()
    return storage, nc

storage, nc = asyncio.run(build_storage())
print(storage, nc)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher() #storage=storage


# Настройка логирования
logging.basicConfig(level=logging.DEBUG)


async def configurate():
    database = PostgresBuild('postgresql+asyncpg://quest:quest@127.0.0.1/data') # сюда надо будет добавить dns из конфига
    await database.drop_tables(Base)  #Вот это надо раскоментить при первом запуске
    await database.create_tables(Base)
    session = database.session()

    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    scheduler.start()

    storage = TTLCache(maxsize=1000000000, ttl=129600)

    await default_properties_set(session)

    # Регистрация роутеров
    dialogs = get_dialogs()
    routers = get_private_routers()

    # Подключение мидлварей
    dp.update.middleware(TransferObjectsMiddleware())
    work_router.message.outer_middleware(WorksOPMiddleware())
    work_router.callback_query.outer_middleware(WorksOPMiddleware())
    work_dialog.message.outer_middleware(WorksOPMiddleware())
    work_dialog.callback_query.outer_middleware(WorksOPMiddleware())
    help_router.message.outer_middleware(ProfOPMiddleware())
    help_router.callback_query.outer_middleware(ProfOPMiddleware())
    diet_router.message.outer_middleware(DietOPMiddleware())
    diet_router.callback_query.outer_middleware(DietOPMiddleware())
    main_router = include_routers(help_router, diet_router, *routers, *dialogs)
    main_router.message.outer_middleware(PrivateMiddleware())
    main_router.callback_query.outer_middleware(PrivateMiddleware())

    # Конфигурация диалоговых окон (для функционала с которым я работаю)
    dp.include_routers(main_router, *get_not_private())
    setup_dialogs(dp)
    return session, scheduler, storage


# Основная функция для запуска бота
async def main():
    session, scheduler, storage = await configurate()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, _scheduler=scheduler, _session=session, _storage=storage)
    except Exception as e:
        print(e)
    finally:
        await nc.close()
        print('Connection to NATS closed')

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
