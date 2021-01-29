import sys
import time

sys.path.append("..")
import datetime
import json
import openpyxl

import pymongo
import requests


def db_electric():
    arr_time = datetime.datetime.now()
    client = pymongo.MongoClient(
        'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
    db = client.er
    collection = db.errorInfo
    sql = {}
    result = collection.find(sql).sort("time", -1).limit(1)
    for i in result:
        da = i['time'] + datetime.timedelta(hours=8)
        print('mongdb最新数据时间为{}.'.format(da), '当前扫描时间为{}'.format(arr_time))
        a_s = (arr_time - da).seconds
        if a_s >= 600:
            url = 'https://oapi.dingtalk.com/robot/send?access_token=ca899af4dc085a63e605bc79052d673d776da23ec43ee272ff3776c84e44798d'
            content = {
                "msgtype": "text",
                "text": {
                    "content": "mongdb,errorInfo集合,超过10分钟数据未更新！(这次是真的)"
                },
                "at": {
                    "isAtAll": True
                }
            }
            headers = {"Content-Type": "application/json;charset=utf-8"}
            r = requests.post(url=url, headers=headers, json=content)
            print(r.content)


while 1:
    db_electric()
    time.sleep(300)
