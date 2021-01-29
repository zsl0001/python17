from gevent import monkey
import gevent
import random
import requests
import json


def task_1():
    header = {'Content-Type': 'application/json;charset=UTF-8',
              'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwidXNlckNvbXBhbnlOYW1lIjoiIiwicm9sZUlkcyI6IjI1NiIsInVzZXJDb21wYW55aWQiOjI1NiwidXNlclBob25lIjoiMTIzNDUiLCJtb2R1bGUiOiJxaXllIiwiaXNzIjoid2x5dWFuIiwidXNlck5hbWUiOiJhZG1pbiIsImV4cCI6MTYxMTM2NjA2OCwidXNlckNvZGUiOiJhZG1pbiJ9.NQi3xh87JO04t_aVW1VV07SQErmxUmYQNsESnfelsXM'
              }
    count = 351608087669322
    while count < 351608087999999:
        count = count + 1
        data = {"type": "2", "simid": "1", "imeicode": str(count), "simbatch": "", "phoneNo": "", "expiryStarttime": "",
                "expiryEndtime": "", "companyID": 31505, "salerName": "", "temperature": 0,
                "companyName": "北京小蜜蜂婚姻服务有限公司绵阳分公司"}
        res = requests.post(headers=header, data=json.dumps(data), url='http://192.168.1.89:1256/cp/tmsDevices/add')
        print(res.text)


# data = {'type': '2', 'simid': '1', 'imeicode': '351608087500001', 'simbatch': '', 'phoneNo': '', 'expiryStarttime': '', 'expiryEndtime': '', 'companyID': 31505, 'salerName': '', 'temperature': 0, 'companyName': '北京小蜜蜂婚姻服务有限公司绵阳分公司'}
# res = requests.post(headers=header, data=json.dumps(data), url='http://192.168.1.89:1256/cp/tmsDevices/add')
# print(res.text)

if __name__ == "__main__":
    monkey.patch_all()  # 给所有的耗时操作打上补丁
    gevent.joinall([  # 等到协程运行完毕
        gevent.spawn(task_1),  # 创建协程
    ])
