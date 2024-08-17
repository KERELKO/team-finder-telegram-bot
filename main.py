import logging

from telegram import Update
from telegram.ext import Application, CommandHandler

from src.bot.constants import BotCommands
from src.bot.handlers.commands import start_handler, help_handler, find_team_handler
from src.bot.handlers.conversations import (
    CollectUserDataConversation,
    CreateTeamConversation,
    UpdateTeamConversation,
)
from src.common.config import get_conf, RedisConfig


def main() -> None:
    """Start the bot"""
    RedisConfig().create_team_index()
    app = Application.builder().token(get_conf().TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler(BotCommands.START, start_handler))
    app.add_handler(CommandHandler(BotCommands.HELP, help_handler))
    app.add_handler(CommandHandler(BotCommands.FIND_TEAM, find_team_handler))

    app.add_handler(CreateTeamConversation.get_handler(command=BotCommands.CREATE_TEAM))
    app.add_handler(UpdateTeamConversation.get_handler(command=BotCommands.UPDATE_TEAM))
    app.add_handler(CollectUserDataConversation.get_handler(command=BotCommands.CREATE_PROFILE))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logging.getLogger('httpx').setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    main()
