from typing import Callable, Dict, Tuple

from attrdict import AttrDict
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from reservations_bot.models import User, Reservations
from reservations_bot.settings import State


NextMessage = Tuple[str, InlineKeyboardMarkup]


class BaseHandler:
    state_methods: Dict[State, str]

    def __init__(self, call: CallbackQuery, user: User, session: AttrDict):
        self.call: CallbackQuery = call
        self.user: User = user
        self.session: AttrDict = session

    def handle(self) -> NextMessage:
        method_name: str = self.state_methods.get(self.session.state)
        method: Callable = getattr(self, method_name)

        return method()

    def _get_keyboard_with_user_reservation_dates(self) -> InlineKeyboardMarkup:
        user_reservation_dates_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()

        user_reservations: Reservations = self.user.get_reservations()

        for reservation_date in user_reservations:
            date_button: InlineKeyboardButton = InlineKeyboardButton(
                text=str(reservation_date), callback_data=reservation_date.isoformat())

            user_reservation_dates_keyboard.add(date_button)

        return user_reservation_dates_keyboard
