import datetime as dt
from typing import Generator, Iterable, Set, Dict

from attrdict import AttrDict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from reservations_bot.handlers.base import BaseHandler, NextMessage
from reservations_bot.models import WorkspaceID, get_all_reserved_workspaces_for_date
from reservations_bot.office_map import Status, get_workspace_statuses_for_date, get_office_map, \
    get_statuses_with_highlighted_workspace
from reservations_bot.settings import State, EXIT_MESSAGE


class CreateReservationHandler(BaseHandler):
    state_methods = {
        State.IN_MAIN_MENU: "start_reservation",
        State.CHOOSING_RESERVATION_DATE_CREATE: "set_date",
        State.CHOOSING_RESERVATION_WORKSPACE_CREATE: "set_workspace",
    }

    def start_reservation(self) -> NextMessage:
        self.session.state = State.CHOOSING_RESERVATION_DATE_CREATE

        next_text: str = "Выберите дату"
        next_keyboard: InlineKeyboardMarkup = self._get_keyboard_with_reservation_dates()

        return next_text, next_keyboard

    def set_date(self) -> NextMessage:
        data: str = self.call.data

        reservation_date: dt.date = dt.datetime.fromisoformat(data).date()
        session_data: AttrDict = self.session["data"]
        session_data.update(reservation_date=reservation_date)

        return self._prepare_setting_workspace(reservation_date)

    def set_workspace(self):
        data: str = self.call.data
        workspace_id: int = int(data)

        session_data: AttrDict = self.session["data"]
        reservation_date: dt.date = session_data.reservation_date

        if workspace_id in get_all_reserved_workspaces_for_date(reservation_date):  # race condition
            return self._prepare_failure_state(failure_text="Не успели, место уже забронировано(")

        self.user.add_reservation(reservation_date, workspace_id)

        return self._prepare_success_state(reservation_date, workspace_id)

    def _get_keyboard_with_reservation_dates(self) -> InlineKeyboardMarkup:
        dates_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()

        next_week_days: Generator[dt.date] = ((dt.datetime.now() + dt.timedelta(days=days)).date()
                                              for days in range(1, 8))

        user_reserved_days: Iterable[dt.date] = self.user.get_reservations().keys()

        for date in next_week_days:
            if date not in user_reserved_days:
                button: InlineKeyboardButton = InlineKeyboardButton(text=str(date), callback_data=date.isoformat())
                dates_keyboard.add(button)

        return dates_keyboard

    def _prepare_setting_workspace(self, reservation_date: dt.date) -> NextMessage:
        self.session.state = State.CHOOSING_RESERVATION_WORKSPACE_CREATE

        ws_statuses: Dict[WorkspaceID, Status] = get_workspace_statuses_for_date(reservation_date)
        office_map: str = get_office_map(ws_statuses)

        next_message_text: str = "Выберите место\n" + office_map
        free_workspaces_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()

        free_workspaces: Generator[int] = (workspace for workspace, status in ws_statuses.items()
                                           if status == Status.AVAILABLE)

        for workspace in free_workspaces:
            button: InlineKeyboardButton = InlineKeyboardButton(
                text=f"место #{workspace}", callback_data=str(workspace))

            free_workspaces_keyboard.add(button)

        return next_message_text, free_workspaces_keyboard

    def _prepare_success_state(self, reservation_date: dt.date, workspace_id: WorkspaceID) -> NextMessage:
        self.session.state = State.FINISH_CREATE

        workspace_statuses: Dict[WorkspaceID, Status] = get_statuses_with_highlighted_workspace(workspace_id)
        map_with_highlighted_workspace: str = get_office_map(workspace_statuses)

        next_text: str = (map_with_highlighted_workspace + "\n"
                          + f"Успешно забронировано место #{workspace_id} на {reservation_date}")

        exit_keyboard: InlineKeyboardMarkup = self._get_exit_keyboard()

        return next_text, exit_keyboard

    def _prepare_failure_state(self, failure_text):
        self.session.state = State.FINISH_CREATE

        next_text: str = failure_text

        exit_keyboard: InlineKeyboardMarkup = self._get_exit_keyboard()

        return next_text, exit_keyboard
