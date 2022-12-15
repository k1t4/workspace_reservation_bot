import telebot
from telebot import apihelper

from settings import TOKEN

apihelper.ENABLE_MIDDLEWARE = True


reservations_bot = telebot.TeleBot(TOKEN)
