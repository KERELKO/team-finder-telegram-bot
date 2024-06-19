from telegram import Update
from telegram.ext import Application, CommandHandler

from src.bot.handlers.base import start, help_command
from src.bot.handlers.handlers import UserDataCollector
from src.common.config import get_conf


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(get_conf().TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))

    application.add_handler(UserDataCollector.get_handler())

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
