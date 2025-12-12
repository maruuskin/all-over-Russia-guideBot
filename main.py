import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, Updater, ConversationHandler
from config import BOT_TOKEN
from functions import start, hotels_in_city, restaurants, weather_response, sights_in_city, sights_numbers
from db_operators import create_database


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
all_coords = []


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hotels", hotels_in_city))
    application.add_handler(CommandHandler("cafes", restaurants))
    application.add_handler(CommandHandler("weather", weather_response))
    # application.add_handler(text_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('sights', sights_in_city)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, sights_numbers)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    create_database()
    main()
