from aiogram.fsm.state import StatesGroup, State


class ConfigState(StatesGroup):
    waiting_for_age = State()