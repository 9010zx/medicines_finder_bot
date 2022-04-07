import json
import logging
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from medicines_finder.finder import Finder
from medicines_finder.redis_connect import send_to_redis, get_from_redis
from medicines_finder import exc


def send_locaction():
    send_location_btn = KeyboardButton('Send location', request_location=True)
    send_location_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(send_location_btn)
    return send_location_markup

async def generate_drug_forms_keyboard(forms_key):
    forms_keyboard_markup = InlineKeyboardMarkup()
    forms = await get_from_redis(forms_key)
    if not forms:
        raise exc.EmptyFormException
    for form in forms:
        logging.info(form)
        cd = form['form'][:30]
        await send_to_redis(cd, form)
        form_key = InlineKeyboardButton(form['form'], callback_data=cd)
        forms_keyboard_markup.add(form_key)
    return forms_keyboard_markup

def pharmacy_geolocation(koords):
    pharmacy_keyboard_markup = InlineKeyboardMarkup()
    return pharmacy_keyboard_markup.add(
        InlineKeyboardButton('Показать на карте', callback_data=json.dumps(koords))
    )

def find():
    markup = InlineKeyboardMarkup()
    find_btn = InlineKeyboardButton('Начать поиск', callback_data='find')
    return markup.add(find_btn)
