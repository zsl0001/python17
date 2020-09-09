import sys

sys.path.append("..")
from DBUtils.PooledDB import PooledDB
import DB_Pool.db_config as config

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
)


class Connect(object):
    def __init__(self, pool_obj):
        self.conn = pool_obj.connection()

    def close(self,  conn):
        """释放连接归还给连接池"""
        conn.close()


con = Connect(pool)
print(dir(con))
