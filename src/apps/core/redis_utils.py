import redis
import pickle

from functools import wraps
from django.conf import settings


class RedisManager:

    def __init__(self):
        self.redis = redis.Redis(host=settings.REDIS_CONFIG['HOST'], port=settings.REDIS_CONFIG['PORT'])

    def get_conn(self):
        return self.redis

    def close(self):
        self.redis.close()


redis_manager = RedisManager()


def decorator_command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        redis_conn = redis_manager.get_conn()
        return func(redis_conn, *args, **kwargs)

    return wrapper


@decorator_command
def test_conn(redis_conn):
    try:
        redis_conn.ping()
        return True
    except redis.exceptions.ConnectionError as e:
        print(f"Redis Connection Error: {e}")
        return False


@decorator_command
def pack_data(redis_conn, data):
    return pickle.dumps(data)


@decorator_command
def unpack_data(redis_conn, data):
    return pickle.loads(data)


@decorator_command
def set_value(redis_conn, key, value):
    redis_conn.set(key, pack_data(redis_conn, value))
    return True


@decorator_command
def set_value_expire(redis_conn, key, value, seconds):
    redis_conn.set(key, pack_data(redis_conn, value), ex=seconds)
    return True


@decorator_command
def get_value(redis_conn, key):
    val = redis_conn.get(key)
    return unpack_data(redis_conn, val) if val else None


@decorator_command
def remove_key(redis_conn, key):
    redis_conn.delete(key)
    return True


@decorator_command
def clear_db(redis_conn):
    redis_conn.flushdb()
    return True