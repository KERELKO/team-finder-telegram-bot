import logging

from telegram import Update
from telegram.ext import Application, CommandHandler

from team_bot.bot.v1.constants import BotCommand
from team_bot.bot.v1.handlers.commands import start_handler, help_handler, find_team_handler
from team_bot.bot.v1.handlers.conversations import (
    CollectUserDataConversation,
    CreateTeamConversation,
    UpdateTeamConversation,
)
from team_bot.common.config import Config, RedisConfig
from team_bot.infra.di import Container


def main() -> None:
    """Start the bot"""
    container = Container()
    config = container.resolve(Config)
    redis_config = container.resolve(RedisConfig)
    redis_config.create_team_index()
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler(BotCommand.START, start_handler))
    app.add_handler(CommandHandler(BotCommand.HELP, help_handler))
    app.add_handler(CommandHandler(BotCommand.FIND_TEAM, find_team_handler))

    app.add_handler(CreateTeamConversation.get_handler(command=BotCommand.CREATE_TEAM))
    app.add_handler(UpdateTeamConversation.get_handler(command=BotCommand.UPDATE_TEAM))
    app.add_handler(CollectUserDataConversation.get_handler(command=BotCommand.CREATE_PROFILE))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logging.getLogger('httpx').setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    main()
