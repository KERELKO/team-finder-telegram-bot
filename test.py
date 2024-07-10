# type: ignore
from src.common.config import get_conf

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ApplicationBuilder


TOKEN = get_conf().TELEGRAM_BOT_TOKEN


async def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    chat = await context.bot.get_chat(chat_id)
    group_title = chat.title
    print(group_title)
    # if first_message:
    #     await update.message.reply_text(
    #         f"Group Title: {group_title}\nFirst Message: {first_message}"
    #     )
    # else:
    #     await update.message.reply_text(f"Group Title: {group_title}\nNo messages found")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()


if __name__ == '__main__':
    main()
