import sys

sys.path.append("..")
from concurrent.futures.thread import ThreadPoolExecutor
from mongoengine.queryset.visitor import Q
import requests
import datetime
import mongoengine
import json
import pymongo
import pymssql

# host = 'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481'
# db = 'er'
#
# con = mongoengine.connect(db=db, host=host)
#
#
# class smsContent(mongoengine.Document):
#     meta = {
#         'collection': 'smsContent', 'strict': False
#     }
#
#     _id = mongoengine.StringField()
#     _class = mongoengine.StringField()
#     stime = mongoengine.DateTimeField()
#     contact = mongoengine.StringField()
#     content = mongoengine.StringField()
#     orderid = mongoengine.StringField()
#     triggerPoint = mongoengine.DictField()
#     transMode = mongoengine.IntField()
#     smsType = mongoengine.IntField()

# conn = pymssql.connect('172.16.16.23', 'WLY', 'Wly2.techns@907', 'WLY', charset='utf8')
client = pymongo.MongoClient(
    'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
db = client.er
col = db['smsContent']
res = col.find({"orderid": "20092200796"})
for i in res:
    print(i['mark'])

# sql = '''SELECT  * from TMS_OrderIndex where index_Pactcode = 'RLN200922023' and Index_SrcClass = 1 and Index_Status != 32'''
# cursor = conn.cursor(as_dict=True)
# cursor.execute(sql)
# res = cursor.fetchall()
# for i in res:
#     print(i)
