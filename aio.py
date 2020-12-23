from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher import Dispatcher

import logging

from conf import logger_config
from show import Data
import parsing
from models import *

logging.config.dictConfig(logger_config)
logger = logging.getLogger('bot')

API_TOKEN = None # API Token

# webhook settings
WEBHOOK_HOST = None # your host
WEBHOOK_PATH = '/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 3001

# logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(LoggingMiddleware())

shows = {}

cities = {
    'Москва':'moskva', 
    'Санкт-Петербург':'sankt-peterburg',
    'Волгоград':'volgograd',
    'Краснодар':'krasnodar',
    'Казань':'kazan'
}

buttons = {
    'btn_prev': types.InlineKeyboardButton('back', callback_data='prev'), # Preview item
    'btn_next': types.InlineKeyboardButton('next', callback_data='next'), # Next item
    'btn_more': types.InlineKeyboardButton('more', callback_data='more'), # More about item
    'btn_back': types.InlineKeyboardButton('back', callback_data='back'), # Back to items list
    'btn_open': types.InlineKeyboardButton('open', callback_data='open'), # Open in the web # Override with each item
    'btn_forw': types.InlineKeyboardButton('>', callback_data='forw'), # Next photo
    'btn_last': types.InlineKeyboardButton('<', callback_data='last'), # Last photo
}

# Methods handlers below 
@dp.callback_query_handler(lambda c: c.data == 'forw' or c.data == 'last')
async def swiping_callback(callback_query):
    """ The method gets callback from buttons next and preview 
    on the item page to swiping images """
    try:
        msg_id = callback_query['message']['message_id']
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        status, img = shows[msg_id].item.next_img() if callback_query.data == 'forw' else shows[msg_id].item.prev_img()
        # One or two buttons 
        if status == 'first':
            keyboard.add(buttons['btn_forw'])
        elif status == 'last':
            keyboard.add(buttons['btn_last'])
        else:
            keyboard.add(buttons['btn_last'], buttons['btn_forw'])
        # Add other buttons 
        keyboard.add(types.InlineKeyboardButton('open', 
                                    url=shows[msg_id].get_item('url'), 
                                    callback_data='open'))
        keyboard.add(buttons['btn_back'])
        # Action
        await bot.edit_message_media(types.InputMediaPhoto(img), 
                                    callback_query.from_user.id, msg_id)
        await bot.edit_message_caption(callback_query.from_user.id, msg_id, 
                                    caption=shows[msg_id].item.caption, 
                                    reply_markup=keyboard)
    except Exception as e:
        logger.error('Exception text is: \'{}\''.format(e))
        await bot.answer_callback_query(callback_query.id, 
                    'Произошла ошибка, попробуйте снова\nДанные об ошибке отправлены администратору', 
                    show_alert=True)


@dp.callback_query_handler(lambda c: c.data == 'prev' or c.data == 'next')
async def items_callback(callback_query):
    """ The method gets callback from buttons next and preview 
    on the main screen to get last or future item preview """
    try:
        msg_id = callback_query['message']['message_id']
        # Get Status
        status = shows[msg_id].next_item() if callback_query.data == 'next' else shows[msg_id].prev_item()
        # Making keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        if shows[msg_id].get_item('url') is not None: # If object is blank
            keyboard.add(buttons['btn_more']) # Then it's close
        if status == 'first': # If first item
            keyboard.add(buttons['btn_next'])
        elif status == 'last': # If last item
            keyboard.add(buttons['btn_prev'])
        else:
            keyboard.add(buttons['btn_prev'], buttons['btn_next'])
        # Valuarables 
        text = '<b>Название:</b> {}\n<b>Цена:</b> {}'.format(
                                    shows[msg_id].get_item('name'),
                                    shows[msg_id].get_item('price'))
        img = shows[msg_id].get_item('img')
        # Edit above message
        await bot.edit_message_text('Found: {}/{}'.format(
                                    shows[msg_id].get_current_number(), shows[msg_id].count), 
                                    callback_query.from_user.id, shows[msg_id].above)
        # Edit main message
        await bot.edit_message_media(types.InputMediaPhoto(img), 
                                    callback_query.from_user.id, msg_id)
        await bot.edit_message_caption(callback_query.from_user.id, 
                                    msg_id, caption=text, reply_markup=keyboard, 
                                    parse_mode='html')
    except Exception as e:
        logger.error('Exception text is: \'{}\''.format(e))
        await bot.answer_callback_query(callback_query.id, 
                                    'Произошла ошибка, попробуйте снова\nДанные об ошибке отправлены администратору', 
                                    show_alert=True)


@dp.callback_query_handler(lambda c: c.data == 'back')
async def back_callback(callback_query):
    """ The method gets callback from button 'back' 
    on the item page to return on the main screen """
    try: 
        msg_id = callback_query['message']['message_id']
        # Keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(buttons['btn_more'])
        keyboard.add(buttons['btn_prev'], buttons['btn_next'])
        logger.debug("The user {} clicked on 'back'".format(callback_query.from_user.id))
        # Editing messages 
        # Above message
        await bot.edit_message_text('Found: {}/{}'.format(
                                    shows[msg_id].get_current_number(), shows[msg_id].count), 
                                    callback_query.from_user.id, shows[msg_id].above)
        # Item Message
        await bot.edit_message_media(types.InputMediaPhoto(shows[msg_id].get_item('img')), 
                                    callback_query.from_user.id, msg_id)
        await bot.edit_message_caption(callback_query.from_user.id, msg_id, 
                                    caption=shows[msg_id].get_item('name'), reply_markup=keyboard)
    except Exception as e:
        logger.error('Exception text is: \'{}\''.format(e))
        await bot.answer_callback_query(callback_query.id, 
                                    'Произошла ошибка, попробуйте снова\nДанные об ошибке отправлены администратору', 
                                    show_alert=True)


@dp.callback_query_handler(lambda c: c.data == 'more')
async def more_callback(callback_query): # More callback handler
    """ The method gets callback from button 'more'
    on the main screen to open item page """
    try: # Code below may raise an exception
        msg_id = callback_query['message']['message_id']
        url = shows[msg_id].get_item('url')
        # Get data
        shows[msg_id].get_item_data()
        # Forming keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        if len(shows[msg_id].item.images) > 1:
            keyboard.add(buttons['btn_forw'])
        keyboard.add(types.InlineKeyboardButton('open', url=url, callback_data='open'))
        keyboard.add(buttons['btn_back'])
        # Edit above message text
        logger.debug('The user {} clicked on \'more\''.format(callback_query.from_user.id))
        await bot.edit_message_text('<b>Название:</b> {}\n<b>Цена:</b> {}'.format(
                                    shows[msg_id].get_item('name'), shows[msg_id].get_item('price')), 
                                    callback_query.from_user.id, shows[msg_id].above, parse_mode='html')
        # Edit main message 
        await bot.edit_message_media(types.InputMediaPhoto(shows[msg_id].item.get_img()), 
                                    callback_query.from_user.id, msg_id)
        await bot.edit_message_caption(callback_query.from_user.id, msg_id, 
                                    caption=shows[msg_id].item.caption, reply_markup=keyboard)
    except Exception as e:
        logger.error('Exception text is: \'{}\''.format(e))
        await bot.answer_callback_query(callback_query.id, 
                    'Произошла ошибка, попробуйте снова\nДанные об ошибке отправлены администратору', 
                    show_alert=True)


# Commands handlers below 
@dp.message_handler(commands=['start'])
async def registration(message: types.Message):
    session = sessionmaker(bind=engine)()
    if session.query(User).filter(User.user_id == message.from_user.id).count() == 0:
        try:
            user = User(message.from_user.id, "{} {}".format( # Create new user 
                        message.from_user.first_name, message.from_user.last_name))
            session.add(user)
            session.commit()
            logger.info('New user was created. ID: {} Name: {} {}'.format(
                                message.from_user.id, message.from_user.first_name,
                                message.from_user.last_name))
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            keyboard.add(types.KeyboardButton('Волгоград'))
            keyboard.add(types.KeyboardButton('Санкт-Петербург'))
            keyboard.add(types.KeyboardButton('Москва'))
            keyboard.add(types.KeyboardButton('Краснодар'))
            keyboard.add(types.KeyboardButton('Казань'))
            await bot.send_message(message.from_user.id, 'Выберите город', reply_markup=keyboard)
        except Exception as e:
            logger.critical('Database error, exception: [{}]'.format(e))
    else:
        logger.debug('The user {} sent /start command'.format(message.from_user.id))


@dp.message_handler(commands=['region'])
async def set_region(message: types.Message):
    try:
        # Section 1
        session = sessionmaker(bind=engine)()
        user = session.query(User).filter(User.user_id == message.from_user.id).first()
        session.add(user)
        user.region = None
        session.commit()
        # Section 2
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        keyboard.add(types.KeyboardButton('Волгоград'))
        keyboard.add(types.KeyboardButton('Санкт-Петербург'))
        keyboard.add(types.KeyboardButton('Москва'))
        keyboard.add(types.KeyboardButton('Краснодар'))
        keyboard.add(types.KeyboardButton('Казань'))
        await bot.send_message(message.from_user.id, 'Выберите город', reply_markup=keyboard)
    except Exception as e:
        logger.critical('Database error, exception: [{}]'.format(e))


# Simple messages handlers below 
@dp.message_handler() 
async def echo(message: types.Message):
    session = sessionmaker(bind=engine)()
    user = session.query(User).filter(User.user_id == message.from_user.id).first()
    session.add(user)
    # If region is None
    if user.region == None: 
        try:
            user.region = cities[message.text]
            await bot.send_message(message.from_user.id, 
                    'Теперь поиск будет происходить по выбранному городу!', 
                    reply_markup=types.ReplyKeyboardRemove())
            logger.info('The user {} have choose the region: {}'.format(user.user_id, message.text))
        except:
            await bot.send_message(message.from_user.id, 
                    'Города нет в списке. Выберите из списка!')
            logger.debug('The user {} have sent an text message but not a region, text: {}'.format(user.user_id, message.text))
    # If region had choosen the message text is request
    else:
        try: 
            await bot.delete_message(user.user_id, user.message_id)
            await bot.delete_message(user.user_id, shows[user.message_id].above)
        except:
            pass
        data = Data(message.text, user)
        # Forming keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        if data.get_item('url') is not None:
            keyboard.add(buttons['btn_more'])
        if data.count > 1:
            keyboard.add(buttons['btn_next'])
        if data.count == 0:
            msg_id = await bot.send_message(message.from_user.id,
                                'По вашему запросу ничего не найдено!')
        else: 
            # Send above message
            above = await bot.send_message(message.from_user.id, 'Items: 1/{}'.format(data.count))
            data.above = above['message_id']
            # And main message
            msg_id = await bot.send_photo(message.from_user.id,
                                        data.get_item('img'),
                                        '<b>Название:</b> {}\n<b>Цена:</b> {}'.format(
                                                                        data.get_item('name'),
                                                                        data.get_item('price')),
                                        reply_markup=keyboard, parse_mode='html')
            #Keep data\
        user.message_id = msg_id['message_id']
        shows[user.message_id] = data
    session.commit()


# Set up methods below  
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    # logging.warning('Shutting down..')
    # insert code here to run it before shutdown
    # session = sessionmaker(bind=engine)()

    # user = session.query(User).filter(User.user_id == 316432844).first()
    # print("User {} Message {}".format(user.user_id, user.message_id))
    # await bot.delete_message(user.user_id, user.message_id)
    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    # logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
