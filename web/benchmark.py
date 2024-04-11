from database import health_check, connect_db
from config import Config
from cache import Cache

import json
import random
import redis
import time


HOST = ''
PORT = 3306
USERNAME = ""
PASSWORD = ""
DBNAME = ""


service_db = None
cache_conn = None


def get_cache():
    global cache_conn
    if not cache_conn:
        cache_conn = redis.from_url(Config.CACHE_URL)

    return Cache(cache_conn)

def get_db():
    global service_db
    if not service_db or health_check(service_db):
        service_db = connect_db(host=Config.HOST,
                                port=Config.PORT,
                                username=Config.USERNAME,
                                password=Config.PASSWORD,
                                database=Config.DBNAME)

    return service_db


COUNT = 10000
try:
    COUNT = int(sys.argv[1])
except:
    pass


def get_random_id():
    return random.randint(1, 4000000)


def db_benchmark():
    print(f"db benchmark : {COUNT}")
    db = get_db()
    cursor = db.cursor()

    start_time = time.perf_counter()
    for i in range(COUNT):
        query = f"select * from redis_test where id={get_random_id()}"
        cursor.execute(query)
        row = cursor.fetchone()

    end_time = time.perf_counter()
    print(f"time elapsed : {int(round((end_time - start_time) * 1000))}ms")


def cache_benchmark():
    print(f"cache benchmark : {COUNT}")
    cache = get_cache()

    start_time = time.perf_counter()
    for i in range(COUNT):
        row = cache.get(Cache.TKEY, str(i))

    end_time = time.perf_counter()
    print(f"time elapsed : {int(round((end_time - start_time) * 1000))}ms")


cache_benchmark()
