from flask import Flask, jsonify
from flask_restx import Api, Resource, reqparse
from database import health_check, connect_db
from config import Config
from cache import Cache

import json
import redis


HOST = 'charsyam.iptime.org'
PORT = 23306
USERNAME = "redis_test"
PASSWORD = "redis_test_2024"
DBNAME = "redis_test"


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


app = Flask(__name__)

api = Api(app, version='1.0', title='API 문서', description='Swagger 문서', doc="/api-docs")


class NotFoundKeyException(Exception):
    pass


@app.errorhandler(Exception)
def global_exception_handler(e):
    code = 500
    message = "Error"

    if isinstance(e, NotFoundKeyException):
        message = "NotFoundKeyException"
    else:
        pass

    return {
        "error": str(e),
        "code": code,
        "message": message
    }


@api.route('/api/key/v1/key/<int:tkey_id>')
class FindKey(Resource):
    def get(self, tkey_id):
        db = get_db()
        cursor = db.cursor()
        query = f"select * from redis_test where id = {tkey_id}"
        cursor.execute(query)
        row = cursor.fetchone()

        if row == None:
            raise NotFoundKeyException()

        resp = {
            "id": row[0],
            "key": row[1],
            "value": row[2]
        }

        return resp


def find_tkey(db, tkey_id):
    cursor = db.cursor()
    query = f"select * from redis_test where id = {tkey_id}"
    cursor.execute(query)
    return cursor.fetchone()


@api.route('/api/key/v1/cache_key/<int:tkey_id>')
class FindCacheKey(Resource):
    def get(self, tkey_id):
        db = get_db()
        cache = get_cache()
    
        resp = cache.get(Cache.TKEY, str(tkey_id))
        if not resp:
            row = find_tkey(db, tkey_id)
            if not row:
                raise NotFoundKeyException()

            resp = json.dumps({
                "id": row[0],
                "key": row[1],
                "value": row[2]
            })

            cache.set(Cache.TKEY, str(tkey_id), resp)

        return json.loads(resp)


if __name__ == '__main__':
    app.run()
