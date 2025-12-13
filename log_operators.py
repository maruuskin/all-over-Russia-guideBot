import os
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes


def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_filename = datetime.now().strftime("%Y_%m_%d.log")
    log_path = os.path.join('logs', log_filename)

    formatter = logging.Formatter('%(asctime)s;%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger = logging.getLogger('telegram_bot')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger


bot_logger = setup_logging()


def log_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str = None):
    try:
        user = update.effective_user
        user_id = user.id if user else "unknown"
        username = user.username if user and user.username else "no_username"
        try:
            log_message = f"{username};{user_id};{action};{context.args[0]}"
        except:
            log_message = f"{username};{user_id};{action}"
        bot_logger.info(log_message)

    except Exception as e:
        print(f"Ошибка при логировании: {e}")



async def log_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        log_user_action(update, context, update.message.text)
    return None