import settings
from bot import reservations_bot
import sys
import runpy


if __name__ == "__main__":
    print(sys.path)
    for module in settings.HANDLERS:
        runpy.run_module(module)

    reservations_bot.infinity_polling()

