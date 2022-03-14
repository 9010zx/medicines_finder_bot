import json
import redis


r = redis.Redis(
    host='127.0.0.1',
    port=6379,
)
def send_to_redis(key, value):
    r.set(key, value)


def get_from_redis(key):
    return json.loads(r.get(key))
