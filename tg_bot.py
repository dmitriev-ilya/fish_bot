import os
import logging
import redis
import textwrap

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, CallbackContext

from elasticpath_api_tools import get_access_token, get_products, get_product, get_file_href, add_cart_item, get_cart_items, remove_product_from_cart, create_customer


_database = None


def send_fish_menu(milton_access_token):
    products = get_products(milton_access_token)['data']
    keyboard = [[]]
    for product in products:
        inline_item = InlineKeyboardButton(product['attributes']['name'], callback_data=product['id'])
        keyboard[0].append(inline_item)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def send_cart_description(milton_access_token, cart_id):
    message = ''
    keyboard = [
        [],
        [
            InlineKeyboardButton('Оплатить', callback_data='pay'),
            InlineKeyboardButton('В меню', callback_data='back')
        ]
    ]
    cart_items = get_cart_items(milton_access_token, cart_id)
    for cart_item in cart_items['data']:
        product = get_product(milton_access_token, cart_item['product_id'])
        product_description = product['data']['attributes'].get('description', 'Нет описания :(')
        item_price = cart_item['meta']['display_price']['with_tax']['unit']['formatted']
        cart_item_cost = cart_item['meta']['display_price']['with_tax']['value']['formatted']

        cart_item_description = f"""
            {cart_item['name']}
            {product_description}
            {item_price} per kg
            {cart_item['quantity']} kg in cart for {cart_item_cost}
        """
        message += textwrap.dedent(cart_item_description)

        keyboard[0].append(InlineKeyboardButton(
            f'Убрать из корзины {cart_item["name"]}',
            callback_data=cart_item['id'])
        )
    total_price = cart_items['meta']['display_price']['with_tax']['formatted']
    message += f'\nTotal: {total_price}'
    reply_markup = InlineKeyboardMarkup(keyboard)

    return message, reply_markup


def start(update: Update, context: CallbackContext, milton_access_token):
    reply_markup = send_fish_menu(milton_access_token)
    update.message.reply_text(
        text='Привет! Ознакомся с нашим ассортиментом!',
        reply_markup=reply_markup
    )
    return 'HANDLE_MENU'


def get_product_description(update: Update, context: CallbackContext, milton_access_token):
    product_id = update.callback_query.data
    product = get_product(milton_access_token, product_id)['data']
    main_image_id = product['relationships']['main_image']['data']['id']
    file_href = get_file_href(milton_access_token, main_image_id)
    fish_description = f"""
        {product['attributes']['name']}

        {product['attributes'].get('description', 'Нет описания :(')}
    """

    keyboard = [
        [
            InlineKeyboardButton('1 кг', callback_data=f'1 {product_id}'),
            InlineKeyboardButton('5 кг', callback_data=f'5 {product_id}'),
            InlineKeyboardButton('10 кг', callback_data=f'10 {product_id}'),
        ],
        [
            InlineKeyboardButton('Назад', callback_data='back'),
            InlineKeyboardButton('Корзина', callback_data='cart')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=file_href,
        caption=textwrap.dedent(fish_description),
        reply_markup=reply_markup
    )
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.callback_query.message.message_id,
    )
    return 'HANDLE_DESCRIPTION'


def description_handler(update: Update, context: CallbackContext, milton_access_token):
    cart_id = update.effective_chat.id
    data = update.callback_query.data
    if data == 'back':
        reply_markup = send_fish_menu(milton_access_token)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Наш ассортимент:',
            reply_markup=reply_markup
        )
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        return 'HANDLE_MENU'
    elif data == 'cart':
        message, reply_markup = send_cart_description(milton_access_token, cart_id)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup
        )
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        return 'HANDLE_CART'
    else:
        quantity, product_id = data.split()

        add_cart_item(
            milton_access_token,
            cart_id,
            str(product_id),
            int(quantity)
        )

    return 'HANDLE_DESCRIPTION'


def cart_handler(update: Update, context: CallbackContext, milton_access_token):
    cart_id = update.effective_chat.id
    data = update.callback_query.data
    if data == 'back':
        reply_markup = send_fish_menu(milton_access_token)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Наш ассортимент:',
            reply_markup=reply_markup
        )
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        return 'HANDLE_MENU'
    elif data == 'pay':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Пожалуйста, введите ваш E-mail:'
        )
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        return 'WAITING_EMAIL'
    else:
        remove_product_from_cart(milton_access_token, cart_id, data)
        message, reply_markup = send_cart_description(milton_access_token, cart_id)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup
        )
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        return 'HANDLE_CART'


def email_handler(update: Update, context: CallbackContext, milton_access_token):
    cart_id = update.effective_chat.id
    email = update.message.text

    create_customer(milton_access_token, cart_id, email)

    reply_markup = send_fish_menu(milton_access_token)
    text = f"""Ваш заказ успешно создан. Наш менеджер свяжется с вами в ближайшее время. Ваш E-mail: {email}. 
    Вы можете оформить другой заказ в меню ниже:"""
    update.message.reply_text(
        text=textwrap.dedent(text),
        reply_markup=reply_markup
    )
    return 'HANDLE_MENU'


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
        'HANDLE_MENU': get_product_description,
        'HANDLE_DESCRIPTION': description_handler,
        'HANDLE_CART': cart_handler,
        'WAITING_EMAIL': email_handler
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