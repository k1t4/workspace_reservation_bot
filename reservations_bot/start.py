import settings
from bot import reservations_bot

import runpy


if __name__ == "__main__":
    for module in settings.HANDLERS:
        runpy.run_module(module)

    reservations_bot.infinity_polling()

