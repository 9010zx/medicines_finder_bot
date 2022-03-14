import json
import logging
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from medicines_finder.finder import get_drug_forms


send_location_btn = KeyboardButton('Send location', request_location=True)
send_location_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(send_location_btn)

def generate_drug_forms_keyboard(data):
    forms_keyboard_markup = InlineKeyboardMarkup()
    for form, cd in get_drug_forms(data):
        form_key = InlineKeyboardButton(form, callback_data=cd)
        forms_keyboard_markup.add(form_key)
        logging.info(form)
    return forms_keyboard_markup

