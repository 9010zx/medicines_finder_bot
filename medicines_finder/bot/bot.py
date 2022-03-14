import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import ALL_APTEKI, BOT_TOKEN_API
from medicines_finder.finder import Finder
from medicines_finder.bot import keyboard as kb
from socketio import AsyncClient

from medicines_finder.redis_connect import get_from_redis




logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
sio = AsyncClient()

class DrugStates(StatesGroup):
    drug_forms = State()

@dp.message_handler(commands=['start'])
async def send_hello(message: types.Message):
    await message.answer(
        'Привет! Напиши название лекарства и я попробую найти его поблизости'
    )

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await sio.disconnect()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler()
async def find_forms(message: types.Message):
    await sio.connect(ALL_APTEKI)
    finder = Finder()
    sio.on('search_lekarstva_answer', finder.store_recived_msg)
    await sio.emit('search_lekarstva', Finder.get_search_dict(message.text))
    await asyncio.sleep(2)
    await DrugStates.drug_forms.set()
    await message.answer(
        'Выбери необходимую форму выпуска',
        reply_markup=kb.generate_drug_forms_keyboard(finder.recived_msg))

@dp.callback_query_handler(state=DrugStates.drug_forms)
async def choose_form(callback_query: types.CallbackQuery, state: FSMContext):
    finder = Finder()
    form_json = get_from_redis(callback_query.data)
        
    sio.on('form_lvl_2_answer', finder.store_recived_msg)
    await sio.emit(
        'form_lvl_2', 
        Finder.get_search_dict_lvl_2(form_json['cdprep'], form_json['cdform']))
    await asyncio.sleep(2)
    logging.info(finder.recived_msg)
    await sio.disconnect()
    await bot.send_message(callback_query.from_user.id, finder.prepare_msg())