import telebot

from settings import TOKEN

reservations_bot = telebot.TeleBot(TOKEN, use_class_middlewares=True)
