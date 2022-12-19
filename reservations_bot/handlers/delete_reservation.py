from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from reservations_bot.handlers.base import BaseHandler, NextMessage
from reservations_bot.settings import State, EXIT_MESSAGE
import datetime as dt


class DeleteReservationHandler(BaseHandler):
    state_methods = {
        State.IN_MAIN_MENU: "start_reservation_deletion",
        State.CHOOSING_RESERVATION_DATE_DELETE: "set_reservation_date_to_delete",
    }

    def start_reservation_deletion(self) -> NextMessage:
        next_text: str = "Выберите дату для удаления брони"
        dates_keyboard: InlineKeyboardMarkup = self._get_keyboard_with_user_reservation_dates()

        self.session.state = State.CHOOSING_RESERVATION_DATE_DELETE

        return next_text, dates_keyboard

    def set_reservation_date_to_delete(self) -> NextMessage:
        reservation_date: dt.date = dt.date.fromisoformat(self.call.data)
        self.user.remove_reservation(reservation_date)

        return self._prepare_delete_success_page(reservation_date)

    def _prepare_delete_success_page(self, reservation_date) -> NextMessage:
        self.session.state = State.FINISH_DELETE

        next_message = f"Бронь на {reservation_date} успешно удалена"

        exit_keyboard: InlineKeyboardMarkup = self._get_exit_keyboard()

        return next_message, exit_keyboard
