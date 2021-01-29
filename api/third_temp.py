import os
import sys
import time
from time import strftime

import pandas as pd
import pymssql
import requests

sys.path.append("..")
from models import db, TMSDevice, TMSCompany, TMSSale, StockLog, User, TMSOrderIndex, ReceiptLog, TemperatureReceipt, \
    TMSOrderIndexSms
from datetime import datetime, timedelta
from myconfig import mgdb, sqldb, api_cfg
from math import *
import json

my_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
download_path = os.path.join(my_path, 'download')


class thirdtemp(db.Model):
    __tablename__ = 'third_temp'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    devId = db.Column(db.String(128))
    longitude = db.Column(db.String(128))
    latitude = db.Column(db.String(128))
    type = db.Column(db.DateTime, default=datetime.now)
    time = db.Column(db.String(128))


data = {"devId": "351608086044851", "bLongitude": 113.7983668, "bLatitude": 37.11131937, "latitude": 37.104951,
        "course": 341, "description": "当前位置在:河北省邢台市信都区G2516(天河山隧道)", "model": 0, "time": "2019-05-19T11:00:55.000Z",
        "type": 2, "speed": 0.0, "enterTime": "2020-09-25T03:29:33.799Z", "longitude": 113.785426}


def add_pos(data):
    res = thirdtemp()
    res.devId = data['devId']
    res.longitude = data['longitude']
    res.latitude = data['latitude']
    res.type = data['type']
    res.time = data['time']
    # timeArray2 = time.localtime(timeStamp/1000)
    # print(timeArray2)
    # print(type(timeArray2))
    # res.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp/1000))
    try:
        db.session.add(res)
        db.session.commit()
    except Exception as e:
        print(e)


res2 = db.session.query(TMSOrderIndex.Index_RootOrderID).filter(TMSOrderIndex.Index_CreatorCompanyID == '31505',
                                                                TMSOrderIndex.Index_CreateTime >= '2021-01-27 18:15:06',
                                                                TMSOrderIndex.Index_SrcClass == 1,
                                                                TMSOrderIndex.Index_ArriveMsgTime >= '2021-01-27 18:15:06').all()

headers = {'Accept': 'application/json, text/plain, */*',
           'Content-Type': 'application/json;charset=UTF-8',
           'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNjI5OTIiLCJ1c2VyQ29tcGFueU5hbWUiOiLljJfkuqzlsI_onJzonILlqZrlp7vmnI3liqHmnInpmZDlhazlj7jnu7XpmLPliIblhazlj7giLCJyb2xlSWRzIjoiNTEyLDEyOCwzMiw4LDIsMSIsInVzZXJDb21wYW55aWQiOjMxNTA1LCJ1c2VyUGhvbmUiOiIxODY3MDA5MDM1NiIsIm1vZHVsZSI6InFpeWUiLCJpc3MiOiJ3bHl1YW4iLCJ1c2VyTmFtZSI6IueOi-Wul-awuCIsImV4cCI6MTYxMTkwNTU1OCwidXNlckNvZGUiOiIifQ.zwUrH6Wp8SSfHtzJWUxfq6UJ34eYGEJiflNqRJQ9iqA'}
for i in res2:
    res3 = db.session.query(TMSOrderIndexSms.Index_Code).filter(TMSOrderIndexSms.Index_RootOrderID ==i[0]).all()
    if res3:
        res = requests.put(headers=headers, url='http://192.168.1.89:1256/tms/orderIndex/{}/sign'.format(i[0]))
        print(i[0], res.text)
