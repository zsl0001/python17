import json
import sys

import requests

sys.path.append("..")
import pandas as pd
import pymongo
from pandas import Series, DataFrame
import datetime
from myconfig import mgdb, sqldb, api_cfg

client = pymongo.MongoClient(host=mgdb['host'])
er = client[mgdb['db']]
log = er['log']
status = er['status']
position = er['position']
sleepNotice = er['sleepNotice']


def get_location_time(t):
    t = t + +datetime.timedelta(hours=8)
    l_t = t.strftime("%Y-%m-%d %H:%M:%S")
    return t


def get_location_time2(t):
    t = t + +datetime.timedelta(hours=8)
    l_t = t.strftime("%Y-%m-%d %H:%M:%S")
    return l_t


def trans_add(lat, lng):
    base_url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=SMm8htpBXtu3Hd4n5XUsQwiUnMGvWdBU&output=json&coordtype=wgs84ll&location='
    location = str(lat) + ',' + str(lng)
    url = base_url + location + '&extensions_poi=1'
    res = requests.get(url)
    d = json.loads(res.text)
    try:
        addr = d['result']['formatted_address']
        pos = d['result']['pois'][0]
        adds_info = '距{}({})约{}米.'.format(pos['name'], pos['direction'], pos['distance'])
        ps = addr + ',' + adds_info
        return ps
    except Exception as e:
        print(e)
        return d


def find_lastHBT(imei):
    print(imei)
    res = status.find({'devId': str(imei)}).sort('date', -1).limit(1)
    b = datetime.datetime.now()
    data = {'Device_Status': '', 'devId': imei, 'gsmLevel': '', 'lithium': '', 'time': ''}
    if status.count_documents({'devId': str(imei)}):
        print(1)
        for i in res:
            print(2)
            data['gsmLevel'] = i['gsmLevel']
            data['lithium'] = i['lithium']
            data['time'] = get_location_time2(i["date"])
            if (b - get_location_time(i["date"])).total_seconds() > 420:
                sleeplog = sleepNotice.find({'imei': str(imei)}).sort('date', -1).limit(1)
                for k in sleeplog:
                    if k['date'] >= i["date"]:
                        data['Device_Status'] = '休眠'
                    else:
                        data['Device_Status'] = '离线'
            else:
                data['Device_Status'] = '在线'
    else:
        if log.find({'imei': str(imei)}).sort('time', -1).limit(1).count():
            res = log.find({'imei': str(imei)}).sort('time', -1).limit(1)
            for i in res:
                print(5)
                print(i['content'])
                data['gsmLevel'] = i['content'].split(',')[1]
                data['lithium'] = i['content'].split(',')[-1]
                data['time'] = get_location_time2(i["time"])
                if (b - get_location_time(i["time"])).total_seconds() > 420:
                    data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '在线'
        else:
            data['gsmLevel'] = 0
            data['lithium'] = 0
            data['Device_Status'] = '离线'
    return data


# 连接数据库
# mongo_url = f'mongodb://{username}:{password}@%{host}:{port}/{db}'
# client = pymongo.MongoClient('localhost',27017)
# 加载库
# ganji = client['ganji']
# 加载collection
# info = ganji['info']
# 加载数据
# data = DataFrame(list(info.find()))
# 删除不想要的字段
# data_new = data.T.drop(['_id','url','title'])
# print(data_new)
# my_list = [{"imei": "351608087063108", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087072141", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087072489", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087081977", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087079047", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087079088", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087084690", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087078858", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087078924", "useraccount": "admin", "username": "超级管理员"},
#            {"imei": "351608087078841", "useraccount": "admin", "username": "超级管理员"}]


def my_info(my_list):
    l = [i['imei'] for i in my_list]
    my_dict = {'imei': l}
    df = pd.DataFrame(my_dict)
    df['info'] = df['imei'].apply(find_lastHBT)
    df = df.drop(columns=['imei']).to_dict(orient='records')
    l = [i['info'] for i in df]
    return l


# a = my_info(my_list)
# print(a)
