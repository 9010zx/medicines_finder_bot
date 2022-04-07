import json
import redis
import logging
from medicines_finder import exc


r = redis.Redis(
    host='127.0.0.1',
    port=6379,
)


async def send_to_redis(key, data):
    logging.info(f'Sending to redis {key} {data}')
    r.set(key, json.dumps(data, ensure_ascii=False))


async def get_from_redis(key):
    data = r.get(key)
    if not data:
        logging.warning('Nothing to do')
        raise exc.EmptyDataException
    logging.info(f'Data from redis: {data}')
    return json.loads(data)


async def remove_from_redis(key):
    logging.info(f'Try to remove: {key}')
    r.delete(key)


async def remove_all_by_user_id(user_id):
    for key in r.scan_iter(match=f'{user_id}*'):
        r.delete(key)
