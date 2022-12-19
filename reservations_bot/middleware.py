from typing import Dict, Union

import telebot
from attrdict import AttrDict
from telebot import CancelUpdate, BaseMiddleware
from telebot.types import Message, CallbackQuery

from bot import reservations_bot
from models import User
from settings import WHITE_LIST, logger

SESSIONS: Dict[int, AttrDict] = {}


def get_or_create_session(telegram_id: int) -> AttrDict:
    session: AttrDict = SESSIONS.get(telegram_id)
    if not session:
        session: AttrDict = AttrDict()
        session.update(data=AttrDict())
        SESSIONS[telegram_id] = session

    return session


class AuthenticationException(Exception):
    pass


class Middleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ["message", "callback_query"]

    def pre_process(self, obj: Union[CallbackQuery, Message], data):
        try:
            self.authenticate_user(reservations_bot, message=obj)
        except AuthenticationException:
            return CancelUpdate()

        reservations_bot.session = get_or_create_session(telegram_id=obj.from_user.id)

    def post_process(self, obj: Union[CallbackQuery, Message], data, exception):
        message = obj.message if isinstance(obj, CallbackQuery) else obj

        if exception:
            logger.error(str(exception))

            error_text: str = "Что-то пошло не так, попробуй еще раз (/start)"
            reservations_bot.edit_message_text(text=error_text, message_id=message.id, chat_id=message.chat.id)

    @staticmethod
    def authenticate_user(bot_instance: telebot.TeleBot, message: Message):
        tg_username: str = message.from_user.username

        if tg_username not in WHITE_LIST:
            bot_instance.reply_to(message, "Извините, мне не разрешают разговаривать "
                                           "с незнакомцами, обратитесь к администратору")
            raise AuthenticationException()

        tg_id: int = message.from_user.id
        bot_instance.internal_user = User(telegram_id=tg_id, name=WHITE_LIST[tg_username])


reservations_bot.setup_middleware(Middleware())
