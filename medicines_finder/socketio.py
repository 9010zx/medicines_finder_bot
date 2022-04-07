import logging
from socketio import AsyncClient
from config import ALL_APTEKI
from medicines_finder.redis_connect import send_to_redis


async def connect_to_allapteki(event, msg, key):
    sio = AsyncClient()
    event_answer = f'{event}_answer'
    if event == 'lekarstva_group_seach':
        event += '_get'
    await sio.connect(ALL_APTEKI)
    logging.info('Connected to allapteki.ru')

    @sio.on(event_answer)
    async def handle_recived_msg(data):
        logging.info(f'Get data from allapteki.ru: {data}')
        await send_to_redis(key, data)
        await sio.disconnect()

    await sio.emit(event, msg)
    await sio.wait()
