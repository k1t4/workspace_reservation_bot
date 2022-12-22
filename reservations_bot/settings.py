import logging
import os
from enum import Enum

TOKEN = os.environ.get("BOT_TOKEN")

WHITE_LIST = {
    "kimtabris": "Никита",
    "MilaLemberg": "Мила",
    "@GnomTv": "Иван",
    "@Pihpoh_Atata": "Дима",
    "@FieryDruid": "Павел",
    "@demidos": "Саша",
    "@MegaMaan": "Дима",
    "@Ekaterina_Khudaya": "Катя",
    "@Kiselq": "Саша",
    "@Konstter": "Костя",
    "@maxsheremeev": "Максим",
    "@Gideon_Ravenor": "Федор",
    "@Izelaw": "Сергей",
    "@Lid_Liderk": "Виктор",
    "@sergeykrupyanko": "Сергей",
    "@Salykin": "Саша",
    "@hpawa": "Паша",
    "@ProofX": "Серега",
    "@dema067": "Владислав",
}

HANDLERS = (
    "middleware",
    "entry_point",
)

REDIS_HOST = "localhost"
REDIS_PORT = 6379


class State(Enum):
    IN_MAIN_MENU = 1

    START_RESERVATION_CREATE = 2
    CHOOSING_RESERVATION_DATE_CREATE = 3
    CHOOSING_RESERVATION_WORKSPACE_CREATE = 4
    FINISH_CREATE = 5

    START_RESERVATION_READ = 6
    CHOOSING_RESERVATION_DATE_READ = 7
    FINISH_READ = 8

    START_RESERVATION_DELETE = 9
    CHOOSING_RESERVATION_DATE_DELETE = 10
    FINISH_DELETE = 11


EXIT_MESSAGE = "exit"


RESERVATIONS_STATES_CREATE = (
    State.START_RESERVATION_CREATE,
    State.CHOOSING_RESERVATION_DATE_CREATE,
    State.CHOOSING_RESERVATION_WORKSPACE_CREATE,
    State.FINISH_CREATE
)

RESERVATIONS_STATES_READ = (
    State.START_RESERVATION_READ,
    State.CHOOSING_RESERVATION_DATE_READ,
    State.FINISH_READ,
)

RESERVATIONS_STATES_DELETE = (
    State.START_RESERVATION_DELETE,
    State.CHOOSING_RESERVATION_DATE_DELETE,
    State.FINISH_DELETE,
)

logger = logging.getLogger('reservations_bot')


WEEK_DAYS = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "воскресенье",
}
