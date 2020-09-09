import requests
import json

'//GET请求'
url = "http://api.map.baidu.com/routematrix/v2/driving?output=json&origins=33.701973,120.122574&destinations=36.8676089544291,117.11915799223345&ak=SMm8htpBXtu3Hd4n5XUsQwiUnMGvWdBU"
# 120.44356797421935,31.574324740029333 F
# 117.11915799223345,36.8676089544291   T
# 4500287544
# http://api.map.baidu.com/routematrix/v2/driving?output=json&origins=31.574324740029333,120.44356797421935&destinations=36.8676089544291,117.11915799223345&ak=SMm8htpBXtu3Hd4n5XUsQwiUnMGvWdBU
# http://api.map.baidu.com/routematrix/v2/driving?output=json&origins=40.01116,116.339303&destinations=39.936404,116.452562&ak=SMm8htpBXtu3Hd4n5XUsQwiUnMGvWdBU


url = 'http://106.14.17.157:7777/api/get_lg/'
data = {
    'code': 'qwer?1234!@#1312',
    'datalist': [{'patcode': 'RLN200617043',
                  'imei': '351608085026933'}]
}
req = requests.post(url=url, data=json.dumps(data))
print(eval(req.text))

url2 = 'http://106.14.17.157:7777/api/get_mp/'
data2 = {
    'code': 'qwer?1234!@#1312',
    'start_time': '2020-06-19 10:36:05',
    'end_time': '2020-06-19 14:36:05',
    'imei': '351608085026933',
}
req2 = requests.post(url=url2, data=json.dumps(data2))
da = eval(req2.text)
for i in da:
    # print(i)
    # print(i['latitude'],i['longitude'])
    t = str(i['latitude']) + ',' + str(i['longitude'])
    url = f"http://api.map.baidu.com/routematrix/v2/driving?output=json&origins={t}&destinations={eval(req.text)[0][0]}&ak=SMm8htpBXtu3Hd4n5XUsQwiUnMGvWdBU"
    res = requests.get(url)
    a = json.loads(res.text)
    # print(a.get('result')[0]['distance']['text'])
    if i['type'] == 0:
        p_type = 'GPS定位'
    else:
        p_type = '基站定位'
    print('{},定位类型为{},距离目的地还剩余{}'.format(i['time'], p_type, a.get('result')[0]['distance']['text']))
