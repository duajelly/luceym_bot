from aiogram import Bot, Dispatcher
from config_reader import config

dp = Dispatcher()
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")