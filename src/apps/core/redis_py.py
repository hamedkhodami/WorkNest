import redis
import pickle

from functools import wraps
from django.conf import settings


REDIS = None
REDIS_CONFIG = settings.REDIS_CONFIG

def create_conn():
    global REDIS
    REDIS = redis.Redis(host=REDIS_CONFIG['HOST'], port=REDIS_CONFIG['PORT'])
    return REDIS

def close_conn():
    if REDIS is not None:
        REDIS.close()

def decorator_command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if REDIS is None:
            create_conn()
        return func(*args, **kwargs)

    return wrapper

@decorator_command
def test_conn():
    try:
        REDIS.ping()
        return True
    except redis.exceptions.ConnectionError as e:
        print(f"Redis Connection Error: {e}")
        return False

@decorator_command
def pack_data(data):
    return pickle.dumps(data)

@decorator_command
def unpack_data(data):
    return pickle.loads(data)

@decorator_command
def set_value(key, value):
    REDIS.set(key, pack_data(value))
    return True

@decorator_command
def set_value_expire(key, value, seconds):
    REDIS.set(key, pack_data(value), ex=seconds)
    return True

@decorator_command
def get_value(key):
    val = REDIS.get(key)
    if val:
        return unpack_data(val)
    return None

@decorator_command
def remove_key(key):
    REDIS.delete(key)
    return True

@decorator_command
def clear_db():
    REDIS.flushdb()
    return True