import datetime as dt
from typing import Dict

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from reservations_bot.handlers.base import BaseHandler, NextMessage
from reservations_bot.models import WorkspaceID
from reservations_bot.office_map import get_statuses_with_highlighted_workspace, Status, get_office_map
from reservations_bot.settings import State, EXIT_MESSAGE


class ReadReservationHandler(BaseHandler):
    state_methods = {
        State.IN_MAIN_MENU: "start_showing_reservations",
        State.CHOOSING_RESERVATION_DATE_READ: "set_date_to_show_reservation"
    }

    def start_showing_reservations(self) -> NextMessage:
        next_text: str = "Выберите дату"
        next_keyboard: InlineKeyboardMarkup = self._get_keyboard_with_user_reservation_dates()

        self.session.state = State.CHOOSING_RESERVATION_DATE_READ

        return next_text, next_keyboard

    def set_date_to_show_reservation(self) -> NextMessage:
        reservation_date: dt.date = dt.date.fromisoformat(self.call.data)
        reserved_workspace: WorkspaceID = self.user.get_reserved_workspace(reservation_date)

        statuses: Dict[WorkspaceID, Status] = get_statuses_with_highlighted_workspace(reserved_workspace)
        map_with_highlighted_workspace: str = get_office_map(statuses)

        next_text: str = f"Ваша бронь на {reservation_date.isoformat()}:\n" + map_with_highlighted_workspace

        exit_button: InlineKeyboardButton = InlineKeyboardButton(text="Главное меню", callback_data=EXIT_MESSAGE)
        exit_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup().add(exit_button)

        self.session.state = State.FINISH_READ

        return next_text, exit_keyboard
