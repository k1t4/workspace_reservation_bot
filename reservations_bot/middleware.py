from typing import Dict

import telebot
from attrdict import AttrDict
from telebot import CancelUpdate
from telebot.types import Message

from bot import reservations_bot
from models import User
from settings import WHITE_LIST

SESSIONS: Dict[int, AttrDict] = {}


def get_or_create_session(telegram_id: int) -> AttrDict:
    session: AttrDict = SESSIONS.get(telegram_id)
    if not session:
        session: AttrDict = AttrDict()
        session.update(data=AttrDict())
        SESSIONS[telegram_id] = session

    return session


@reservations_bot.middleware_handler(update_types=["message"])
def authenticate_user(bot_instance: telebot.TeleBot, message: Message):
    tg_username: str = message.from_user.username

    if tg_username not in WHITE_LIST:
        bot_instance.reply_to(message, "Sorry, I'm now allowed to speak with strangers. Contact my author")
        return CancelUpdate()

    tg_id: int = message.from_user.id
    bot_instance.internal_user = User(telegram_id=tg_id, name=WHITE_LIST[tg_username])


@reservations_bot.middleware_handler(update_types=["message"])
def set_session(bot_instance: telebot.TeleBot, message: Message):
    bot_instance.session = get_or_create_session(telegram_id=message.from_user.id)
