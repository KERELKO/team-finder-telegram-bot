from aiogram import Router, types
from aiogram.filters.command import Command

from team_bot.bot.v2.constants import BotCommand, START_TEXT, HELP_TEXT


router = Router()


@router.message(Command(BotCommand.START))
async def start_command_handler(message: types.Message):
    await message.answer(START_TEXT)


@router.message(Command(BotCommand.HELP))
async def help_command_handler(message: types.Message):
    await message.answer(HELP_TEXT)
