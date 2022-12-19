from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from bot import reservations_bot
from handlers.create_reservation import CreateReservationHandler
from models import User
from reservations_bot.handlers.base import NextMessage
from reservations_bot.handlers.delete_reservation import DeleteReservationHandler
from reservations_bot.handlers.read_reservation import ReadReservationHandler
from reservations_bot.settings import State, EXIT_MESSAGE, RESERVATIONS_STATES_CREATE, RESERVATIONS_STATES_READ, \
    RESERVATIONS_STATES_DELETE, logger


@reservations_bot.message_handler(commands=["start"])
def start(message):
    reservations_bot.session["data"].clear()

    reservations_bot.session.state = State.IN_MAIN_MENU
    start_text, start_keyboard = get_start_message(user=reservations_bot.internal_user)

    reservations_bot.reply_to(message, text=start_text, reply_markup=start_keyboard)


def get_start_message(user: User) -> NextMessage:
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()

    if user.has_reservations():
        show_reservations_button: InlineKeyboardButton = InlineKeyboardButton(
            text="Показать брони", callback_data=str(State.START_RESERVATION_READ.value))
        remove_reservations_button: InlineKeyboardButton = InlineKeyboardButton(
            text="Удалить бронь", callback_data=str(State.START_RESERVATION_DELETE.value))

        keyboard.add(show_reservations_button, remove_reservations_button)

    add_reservations_button: InlineKeyboardButton = InlineKeyboardButton(
        text="Забронировать место", callback_data=str(State.START_RESERVATION_CREATE.value))
    keyboard.add(add_reservations_button)

    start_text = "Выберите действие"

    return start_text, keyboard


@reservations_bot.callback_query_handler(func=lambda call: call.data == EXIT_MESSAGE)
def exit_to_main_menu(call: CallbackQuery):
    reservations_bot.session["data"].clear()

    reservations_bot.session.state = State.IN_MAIN_MENU
    start_text, start_keyboard = get_start_message(user=reservations_bot.internal_user)

    reservations_bot.edit_message_text(text=start_text, reply_markup=start_keyboard, message_id=call.message.id,
                                       chat_id=call.message.chat.id)


@reservations_bot.callback_query_handler(func=lambda call: True)
def entry_point(call: CallbackQuery):
    state: State = reservations_bot.session.state

    if state == State.IN_MAIN_MENU:
        state: State = State(int(call.data))

    if state in RESERVATIONS_STATES_CREATE:
        handler_class = CreateReservationHandler

    elif state in RESERVATIONS_STATES_READ:
        handler_class = ReadReservationHandler

    elif state in RESERVATIONS_STATES_DELETE:
        handler_class = DeleteReservationHandler

    else:
        return

    handler = handler_class(call=call, user=reservations_bot.internal_user, session=reservations_bot.session)
    next_text, next_markup = handler.handle()

    reservations_bot.edit_message_text(text=next_text, reply_markup=next_markup, message_id=call.message.id,
                                       chat_id=call.message.chat.id)
