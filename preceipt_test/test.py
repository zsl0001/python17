import requests
import json
import re

# url1 = 'http://106.14.17.157:7777/api/get_order_res/'
url2 = 'http://106.14.17.157:7777/api/get_test_hbt/'
# url3 = 'http://106.14.17.157:7777/api/get_test_elc/'
# url4 = 'http://192.168.1.52:7777/api/get_mp/'
# url5 = 'http://106.14.17.157:7777/api/get_test_ln/'
# url6 = 'http://106.14.17.157:7777/api/get_test_info/'
# data = {'code': 'qwer?1234!@#1312',
#         'imei': '351608086051039',
#         }
# res = requests.post(url=url2, data=json.dumps(data))
# print(res.text)
# print(json.loads(res.text))
# 351608086051096
# 4
data = {'code': 'qwer?1234!@#1312',
        'imei': 1111,
        'start_time': '2020-08-18 00:00:00',
        'end_time': '2020-08-19 00:00:00'
        }
res = requests.post(url=url2, data=json.dumps(data))
print(json.loads(res.text))
# print(json.loads(res.text)[0])
# print(len(json.loads(res.text)))
# for i in range(len(json.loads(res.text))):
#         imei = json.loads(res.text)[i]['devId']
#         lng = json.loads(res.text)[i]['longitude']  # 经度
#         lat = json.loads(res.text)[i]['latitude']  # 纬度
#         p_time = json.loads(res.text)[i]['time']
#         p_type = json.loads(res.text)[i]['type']
#         print(imei)
# data = {'code': 'qwer?1234!@#1312',
#         'imei': '351608086051096',
#         'tag':'4'
#         }
# res = requests.post(url=url6, data=json.dumps(data))
# print(res.text)
# print(json.loads(res.text))
