import logging
import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage

from team_bot.bot.v2.handlers.commands import router as command_router
from team_bot.common.config import Config, RedisConfig
from team_bot.infra.di import Container


async def main() -> None:
    """Start the bot"""
    container = Container()
    config = container.resolve(Config)
    redis_config = container.resolve(RedisConfig)
    redis_config.create_team_index()

    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

    dp = Dispatcher(storage=RedisStorage(redis=redis_config.get_async_redis_client()))

    dp.include_router(command_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logging.getLogger('httpx').setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    asyncio.run(main())
