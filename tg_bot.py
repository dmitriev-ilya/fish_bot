import os
import logging
import redis

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, CallbackContext

from elasticpath_api_tools import get_access_token, get_products

_database = None


def start(update: Update, context: CallbackContext, milton_access_token):
    products = get_products(milton_access_token)['data']
    keyboard = [[]]
    for product in products:
        inline_item = InlineKeyboardButton(product['attributes']['name'], callback_data=product['id'])
        keyboard[0].append(inline_item)
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(text='Привет! Ознакомся с нашим ассортиментом!', reply_markup=reply_markup)
    return "ECHO"


def button(update: Update, context: CallbackContext, milton_access_token):
    query = update.callback_query
    update.message.reply_text(str(query.data))


def echo(update: Update, context: CallbackContext, milton_access_token):
    if update.message:
        user_reply = update.message.text
    elif update.callback_query:
        user_reply = update.callback_query.data
    context.bot.send_message(chat_id=update.effective_chat.id, text=user_reply)
    return "ECHO"


def handle_users_reply(update: Update, context: CallbackContext):

    db = get_database_connection()

    load_dotenv()

    milton_access_token = get_access_token(os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'ECHO': echo
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context, milton_access_token)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv("DATABASE_PASSWORD")
        database_host = os.getenv("DATABASE_HOST")
        database_port = os.getenv("DATABASE_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()