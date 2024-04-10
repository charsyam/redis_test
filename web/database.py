import pymysql


def connect_db(host, port, username, password, database):
    return pymysql.connect(host=host,
                         port=port,
                         user=username,
                         password=password,
                         database=database,
                        charset='utf8mb4')


def health_check(db):
    try:
        health_query = "select 1"
        cursor = db.cursor()
        cursor.execute(health_query)
    except:
        return False

    return True
