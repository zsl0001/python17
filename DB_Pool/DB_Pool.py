from DBUtils.PooledDB import PooledDB
import api_preceipt.DB_Pool.db_config as config

pool = PooledDB(
    creator=config.DB_CREATOR,
    mincached=config.DB_MIN_CACHED,
    maxcached=config.DB_MAX_CACHED,
    maxshared=config.DB_MAX_SHARED,
    maxconnections=config.DB_MAX_CONNECYIONS,
    blocking=config.DB_BLOCKING,
    maxusage=config.DB_MAX_USAGE,
    setsession=config.DB_SET_SESSION,
    host=config.DB_TEST_HOST,
    user=config.DB_TEST_USER,
    password=config.DB_TEST_PASSWORD,
    database=config.DB_TEST_DBNAME,
    charset=config.DB_CHARSET,
    as_dict=True
)


class Connect(object):
    def __init__(self, pool_obj):
        self.conn = pool_obj.connection()
        self.cursor = self.conn.cursor()

    def find_one(self, query, args=None):
        self.cursor.execute(query, args)
        return self.cursor.fetchone()

    def find_all(self, query, args=None):
        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def insert_one(self, query, args=None):
        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            self.close(self.conn, self.cursor)
            return True
        except:
            self.conn.rollback()
            self.close(self.conn, self.cursor)
            return False

    def close(self, cursor, conn):
        """释放连接归还给连接池"""
        cursor.close()
        conn.close()


def con():
    con = Connect(pool)
    return con
