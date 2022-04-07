import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import BOT_TOKEN_API
from medicines_finder.finder import Finder
from aiogram.dispatcher.filters import Text
from medicines_finder import exc
from medicines_finder import keyboard as kb
from medicines_finder.redis_connect import get_from_redis, remove_all_by_user_id
from medicines_finder.formatter import choosen_form, finded_pharmacy, waiting


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class DrugStates(StatesGroup):
    form_state = State()
    search_state = State()
    location_state = State()


@dp.message_handler(commands=['start'])
async def send_hello(message: types.Message):
    await message.answer(
        'Привет! Жду названия лекарства.',
    )


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await remove_all_by_user_id(message.from_user.id)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state='*')
async def find_forms(message: types.Message, state: FSMContext):
    drug_name = await exc.drug_name_filter(message.text)
    if not drug_name:
        await message.answer(
            'Некорректный зарпос. Попробуй еще раз.'
        )
        return
    finder = Finder(
        user_id=message.from_user.id,
        event='search_lekarstva',
        drug_name=drug_name
    )
    await finder.get_forms()
    try:
        await message.answer(
            'Выберите форму выпуска',
            reply_markup=await kb.generate_drug_forms_keyboard(finder.forms_redis_key)
        )
    except exc.EmptyFormException:
        await message.answer(
            'Не найдены формы выпуска. Попробуй ещё раз.'
        )
        return
    await DrugStates.form_state.set()


@dp.callback_query_handler(text='find', state='*')
async def wait_search_request(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        callback_query.message.chat.id,
        callback_query.message.message_id
    )
    search_request = await get_from_redis(callback_query.from_user.id)
    for drug in search_request:
        await bot.send_message(
            callback_query.from_user.id,
            choosen_form(drug)

        )
    await bot.send_message(
        callback_query.from_user.id,
        f'Для дальнейшего поиска, отправь местолоположение',
        reply_markup=kb.send_locaction()
    )
    await DrugStates.search_state.set()


@dp.callback_query_handler(state=DrugStates.form_state)
async def choose_form(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        callback_query.message.chat.id,
        callback_query.message.message_id
    )
    form_json = await get_from_redis(callback_query.data)
    await bot.send_message(
        callback_query.from_user.id,
        waiting(form_json),
        reply_markup=kb.find()
    )
    await Finder.append_choosen_form(callback_query.from_user.id, form_json)


@dp.message_handler(content_types=['location'], state=DrugStates.search_state)
async def handle_location(message: types.Message, state: FSMContext):
    logging.info(message.location)
    koord = [message.location['latitude'], message.location['longitude']]
    key = await Finder.get_price(message.from_user.id, koord)
    price_list = await get_from_redis(key)
    if price_list:
        for pharmacy in price_list[:2]:
            pharm_koord = [pharmacy['map1'], pharmacy['map2']]
            await message.answer(
                finded_pharmacy(pharmacy),
                reply_markup=kb.pharmacy_geolocation(pharm_koord),
                parse_mode='Markdown'
            )
    else:
        await message.answer('Не найдено аптек по близости. Попробуйте другой запрос.')
    await DrugStates.location_state.set()
    await remove_all_by_user_id(message.from_user.id)  # WARNING!


@dp.callback_query_handler(state=DrugStates.location_state)
async def send_pharmacy_location(callback_query: types.CallbackQuery, state: FSMContext):
    koords = json.loads(callback_query.data)
    logging.info(koords)
    await bot.send_location(
        callback_query.from_user.id,
        latitude=koords[1],
        longitude=koords[0]
    )
