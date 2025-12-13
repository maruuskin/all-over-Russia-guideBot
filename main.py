import logging

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from config import BOT_TOKEN
from functions import start, help, hotels_in_city, restaurants, weather_response, sights_in_city, sights_numbers, \
    get_location_cafes, get_location_hotels, stop
from db_operators import create_database
from log_operators import log_all_messages, setup_logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        log_all_messages
    ), group=1)

    application.add_handler(CommandHandler("start", start), group=0)
    application.add_handler(CommandHandler("help", help), group=0)
    application.add_handler(CommandHandler("weather", weather_response), group=0)

    conv_handler_sights = ConversationHandler(
        entry_points=[CommandHandler('sights', sights_in_city)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, sights_numbers)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler_sights)

    conv_handler_cafes = ConversationHandler(
        entry_points=[CommandHandler('cafes', restaurants)],

        states={
            1: [MessageHandler(filters._Location(), get_location_cafes)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler_cafes)

    conv_handler_hotels = ConversationHandler(
        entry_points=[CommandHandler('hotels', hotels_in_city)],

        states={
            2: [MessageHandler(filters._Location(), get_location_hotels)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler_hotels)

    application.run_polling()


if __name__ == '__main__':
    bot_logger = setup_logging()
    create_database()
    main()
