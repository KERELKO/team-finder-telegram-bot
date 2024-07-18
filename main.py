from telegram import Update
from telegram.ext import Application, CommandHandler

from src.bot.constants import BotCommands
from src.bot.handlers import find_command
from src.bot.handlers.base import start, help_command
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

    app.add_handler(CommandHandler(BotCommands.START, start))
    app.add_handler(CommandHandler(BotCommands.HELP, help_command))
    app.add_handler(CommandHandler(BotCommands.FIND_TEAM, find_command))

    app.add_handler(CreateTeamConversation.get_handler(command=BotCommands.CREATE_TEAM))
    app.add_handler(UpdateTeamConversation.get_handler(command=BotCommands.UPDATE_TEAM))
    app.add_handler(CollectUserDataConversation.get_handler(command=BotCommands.CREATE_PROFILE))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
