from pymongo import MongoClient
from DBUtils.PooledDB import PooledDB

pool = PooledDB(creator=MongoClient, host='192.168.1.168', username="wangcan", password="123456")
# conn的使用和常规DB-API 2接口类似
conn = pool.connection()
print(conn)