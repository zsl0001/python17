import time

import requests
from locust import HttpLocust, TaskSet, task
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json

import requests

pactCode = 202001250001
data = {
    "underLine": 1,
    "save": 1,
    "createTime": "",
    "srcClass": 1,
    "customerID": 91847,
    "name": "北京小蜜蜂婚姻服务有限公司绵阳分公司",
    "pactCode": "202001250001",
    "code": "",
    "pick": 0,
    "onLoad": 0,
    "fromMan": "1350000111",
    "fromContact": "13577764444",
    "fromTime": "2021-01-25 00:00:00",
    "fromProvince": 110000,
    "fromCity": 110100,
    "fromDistrict": 110101,
    "from": "天安门",
    "addID": "",
    "fromLocation": "116.40384710616807,39.91552563252131",
    "fromManID": "",
    "delivery": 0,
    "offLoad": 0,
    "toContact": "18670090356",
    "toMan": "吾悦广场",
    "toDataNum": 2,
    "toTime": "2021-01-27 23:59:59",
    "endUserName": "测试",
    "endUserID": 0,
    "to": "吾悦广场",
    "toProvince": 410000,
    "toCity": 410100,
    "toDistrict": 410102,
    "toLocation": "113.61947551693958,34.754450781329179",
    "carType": 0,
    "carLength": 0,
    "carVolume": "",
    "carWeight": "",
    "carCount": 1,
    "trackType": 1,
    "deviceCode": "",
    "additionTransportType": "0",
    "flightNo": "",
    "flightDate": "",
    "trainNo": "",
    "trainDate": "",
    "trainStartPlace": "",
    "trainEndPlace": "",
    "deviceId": "",
    "insurance": 0,
    "chargeMode": 2,
    "priceUnit": 3,
    "transportMode": 1,
    "customerSymbolName": "",
    "customerSymbolID": 0,
    "goodsCategory": [1],
    "packageMode": 1,
    "description": "",
    "goodslist": [{
        "goodsLstGoodsID": 247701,
        "goodsLstName": "111",
        "goodsLstWeight": 11,
        "goodsLstVolume": 11,
        "goodsLstQty": 11,
        "goodsLstPrice": 11,
        "goodsLstBatchNo": "",
        "goodsLstComments": "",
        "goodsprice": 1,
        "spc": "1",
        "weight": 1,
        "volume": 1
    }],
    "weightAddition": 0,
    "volumeAddition": 0,
    "goodsValue": "11.00",
    "totalWeight": "11.00",
    "totalVolume": "11.00",
    "totalQty": 0,
    "attach": [],
    "fromType": "1",
    "toType": "0",
    "totalAmount": 11,
    "createType": 0
}

imei = 351608087500000


# key_sh = " "
class my_re(TaskSet):

    @task(1)
    def add_order(self):
        global imei, pactCode
        data['deviceCode'] = str(imei)
        data['pactCode'] = str(pactCode)
        imei = imei + 1
        pactCode = pactCode + 1
        headers = {'Accept': 'application/json, text/plain, */*',
                   'Content-Type': 'application/json;charset=UTF-8',
                   'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNjI5OTIiLCJ1c2VyQ29tcGFueU5hbWUiOiLljJfkuqzlsI_onJzonILlqZrlp7vmnI3liqHmnInpmZDlhazlj7jnu7XpmLPliIblhazlj7giLCJyb2xlSWRzIjoiNTEyLDEyOCwzMiw4LDIsMSIsInVzZXJDb21wYW55aWQiOjMxNTA1LCJ1c2VyUGhvbmUiOiIxODY3MDA5MDM1NiIsIm1vZHVsZSI6InFpeWUiLCJpc3MiOiJ3bHl1YW4iLCJ1c2VyTmFtZSI6IueOi-Wul-awuCIsImV4cCI6MTYxMTY0MDc2OCwidXNlckNvZGUiOiIifQ.LYFmTsYJ_lFh5QnbhN2xkpeEkyPfRZbghAcwOODbMTM'}
        res = self.client.post(headers=headers, data=json.dumps(data),
                               url='/order/createOrder')
        time.sleep(1)
        print(res.text)


class websitUser(HttpLocust):
    task_set = my_re
    host = "http://192.168.1.89:1256/tms"
    min_wait = 3000  # 单位为毫秒
    max_wait = 6000  # 单位为毫秒m
