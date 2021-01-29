import time

import datetime
import redis
import uuid
from gevent import monkey
import gevent

ip = '192.168.1.45'


def get_db(db):
    r1 = redis.Redis(host=ip, port=6379, db=db, decode_responses=True)  # redis默认连接db0
    return r1


c = 0
m = []
for i in range(10):
    l = []
    re1 = get_db(i)
    for k in re1.keys():
        if k.startswith('SMS'):
            l.append(k)
    for j in l:
        c = c + len(re1.hkeys(j))
        m = m + re1.hkeys(j)
print(len(m))
mm = []
with open(r'D:\PycharmProjects\python17\api_preceipt\receipt\online\1.txt', 'r') as f:
    for i in f.readlines():
        if None != i:
            # 从文件中读取行数据时，会带换行符，使用strip函数去掉 换行符后存入列表
            mm.append(i.strip("\n"))
print(mm)
print(len(mm))
ret3 = list(set(mm) ^ set(m))
print(len(ret3))
ret3.sort()
print(ret3)

# re1 = get_db(0)
# print(len(re1.keys()))
# print(re1.keys())
# for i in re1.keys():
#     if i.startswith('SMS'):
#         l.append(i)
# print(len(l))
# print(len(re1.hkeys('SMS:351608087500000')))
#
# def get_uid():
#     return uuid.uuid1().hex
#
#
# def add_my_po():
#     a = datetime.datetime.now()
#     longitude = 116.414789
#     latitude = 39.91146
#     imei = 351608087500000
#     count = 0
#     while count < 10000000:
#         last_end = str(imei)[-1]
#         count = count + 1
#         col = 'position' + last_end
#         print(col)
#         longitude = longitude + 0.00001
#         latitude = latitude + 0.00001
#         my_data = {
#             "devId": str(imei),
#             # "_class": "com.yellows.mongo.dao.model."+ col,
#             "longitude": longitude,
#             "latitude": latitude,
#             "bLongitude": longitude,
#             "bLatitude": latitude,
#             "model": 0,
#             "type": 0,
#             "mcc": 2,
#             "mnc": 0,
#             "lac": 0,
#             "cellId": 0,
#             "time": time.mktime((a + datetime.timedelta(seconds=1)).timetuple()),
#             "course": 122,
#             "speed": 122.0
#         }
#         #  un_time = time.mktime(dtime.timetuple())
#         my_db = str(imei)[-1]
#         r1 = redis.Redis(host=ip, port=6379, db=my_db, decode_responses=True)
#         my_key = 'position:' + str(imei) + str(uuid.uuid1().hex)
#         r1.set(my_key, str(my_data), ex=2626560)
#         print(r1.get(my_key))
#         imei = imei + 1
#         r1.close()
#
#
# add_my_po()
import json

import requests


def add_order():
    pactCode = 20210127000001
    imei = 351608087500001
    for i in range(100000):
        data = {"underLine": 1, "save": 1, "createTime": "", "srcClass": 1, "customerID": 91847,
                "name": "北京小蜜蜂婚姻服务有限公司绵阳分公司", "pactCode": ' ', "code": "", "pick": 0, "onLoad": 0,
                "fromMan": "1867009035", "fromContact": "18670090356", "fromTime": "2021-01-27 00:00:00",
                "fromProvince": 320000, "fromCity": 320100, "fromDistrict": 320114, "from": "吾悦广场", "addID": "",
                "fromLocation": "118.78544536405718,31.997858805465648", "fromManID": "", "delivery": 0, "offLoad": 0,
                "toContact": "18670090356", "toMan": "1867009035", "toDataNum": 30, "toTime": "2021-02-26 23:59:59",
                "endUserName": "长沙", "endUserID": 0, "to": "麓谷企业广场", "toProvince": 430000, "toCity": 430100,
                "toDistrict": 430104, "toLocation": "112.90885490940379,28.2017729779679", "carType": 0, "carLength": 0,
                "carVolume": 0, "carWeight": 0, "carCount": 1, "trackType": 1, "deviceCode": "  ",
                "additionTransportType": "0", "flightNo": "", "flightDate": "", "trainNo": "", "trainDate": "",
                "trainStartPlace": "", "trainEndPlace": "", "deviceId": ' ', "insurance": 0, "chargeMode": 2,
                "priceUnit": 3, "transportMode": 1, "customerSymbolName": "", "customerSymbolID": 0,
                "goodsCategory": [1], "packageMode": 1, "description": "", "goodslist": [
                {"goodsLstGoodsID": 247701, "goodsLstCode": "null", "goodsLstName": "111", "typeName": "飞机",
                 "goodsLstWeight": 111111, "goodsLstVolume": 111111, "weight": 1, "volume": 1, "goodsLstQty": 111111,
                 "goodsLstPrice": 111111, "goodsprice": 1, "goodsLstBatchNo": "", "goodsLstComments": "",
                 "unitName": "立方米",
                 "spc": "1", "goodsLstUnit": 3}], "weightAddition": 0, "volumeAddition": 0, "goodsValue": "111111.00",
                "totalWeight": "111111.00", "totalVolume": "111111.00", "totalQty": 0, "attach": [],
                "totalAmount": 111111, "fromType": "0", "toType": "1", "verifyTime": "", "createType": 0,
                'deviceCode': str(imei), 'pactCode': str(pactCode)}
        imei = imei + 1
        pactCode = pactCode + 1
        headers = {'Accept': 'application/json, text/plain, */*',
                   'Content-Type': 'application/json;charset=UTF-8',
                   'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNjI5OTIiLCJ1c2VyQ29tcGFueU5hbWUiOiLljJfkuqzlsI_onJzonILlqZrlp7vmnI3liqHmnInpmZDlhazlj7jnu7XpmLPliIblhazlj7giLCJyb2xlSWRzIjoiNTEyLDEyOCwzMiw4LDIsMSIsInVzZXJDb21wYW55aWQiOjMxNTA1LCJ1c2VyUGhvbmUiOiIxODY3MDA5MDM1NiIsIm1vZHVsZSI6InFpeWUiLCJpc3MiOiJ3bHl1YW4iLCJ1c2VyTmFtZSI6IueOi-Wul-awuCIsImV4cCI6MTYxMTgxMTE3MSwidXNlckNvZGUiOiIifQ.uKhEwaLixi5AFKqlVxvyCuIIy7eicJ_FmqySSIcaF-8'}
        res = requests.post(headers=headers, data=json.dumps(data),
                            url='http://192.168.1.89:1256/tms/order/createOrder')
        # print(data)
        print(res.text)


# add_order()