import sys

sys.path.append("..")
import copy
import datetime
import json

import pymongo
import requests
from bson import json_util
from myconfig import sqldb, mgdb, api_cfg
from my_db.my_sql import my_sql

my_sql = my_sql(**sqldb)
# print(mgdb)


class my_mog():

    def trans_add(self, lat, lng):
        base_url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=SMm8htpBXtu3Hd4n5XUsQwiUnMGvWdBU&output=json&coordtype=wgs84ll&location='
        location = str(lat) + ',' + str(lng)
        url = base_url + location
        res = requests.get(url)
        d = json.loads(res.text)
        addr = d['result']['formatted_address']
        return addr

    def __init__(self):
        self.client = pymongo.MongoClient(host=mgdb['host'])
        self.db = self.client.er

    # client = pymongo.MongoClient('mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
    # 连接所需数据库,er为数据库名
    def find_status(self, imei=None):  # 查询是否在线
        l = []
        imei = str(imei)
        sql = {'devId': imei}
        collection = self.db.status
        count = collection.count_documents(sql)
        result = collection.find(sql).sort("date", -1)
        if count > 0:
            for i in result:
                l.append(i)
                a = l[0]['date']
                b = datetime.datetime.now()
                if (b - a).total_seconds() > 420:
                    return '在线'
                else:
                    return '不在线'
        else:
            return '暂无数据'

    def find_last_postion(self, imei=None):  # 查询单个设备最后一次定位
        l = []
        collection = self.db.position
        imei = str(imei)
        sql = {'devId': imei}
        count = collection.count_documents(sql)
        result = collection.find(sql).sort("time", -1)
        if count > 0:
            for i in result:
                l.append(i)
            t = l[0]['time']
            a = self.get_location_time(t)
            l[0]['time'] = a
            return l[0]
        else:
            return 0

    def find_more_postion(self, imei=None, start_time=None, end_Time=None):  # 查询单个设备某个时间点的定位数据
        l = []
        collection = self.db.position
        startTime = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(end_Time, '%Y-%m-%d %H:%M:%S')
        imei = str(imei)
        sql = {'devId': imei, 'time': {'$gte': startTime, '$lte': endTime}}
        count = collection.count_documents(sql)
        result = collection.find(sql)
        if count > 0:
            for i in result:
                i['time'] = self.get_location_time(i['time'])
                i = json_util.dumps(i)
                l.append(copy.copy(i))
            return l
        else:
            return '暂无数据'

    def db_electric(self, imei):

        collection = self.db.log

        sql = {'imei': imei}

        l = []
        result = collection.find(sql).sort("time", -1).limit(1)
        data = {
            'imei': '',
            'content': '',
            'time': ''
        }
        for i in result:
            # t = datetime.utcfromtimestamp(int(time.mktime(i['time'].timetuple())))
            data['imei'] = i['imei']
            data['content'] = i['content']
            da = i['time'] + datetime.timedelta(hours=8)
            data['time'] = da.strftime("%Y-%m-%d %H:%M:%S")

            l.append(data.copy())

        return l

    def find_sleep(self, imei=None, start_time=None, end_Time=None):  # 查询单个设备某个时间点的休眠记录
        l = []
        data = {
            "time": "",
            "duration": "",
            "lit": ""
        }
        collection = self.db.sleepNotice
        collection_p = self.db.position
        collection_s = self.db.status
        startTime = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(end_Time, '%Y-%m-%d %H:%M:%S')
        imei = str(imei)
        sql = {'imei': imei, 'date': {'$gte': startTime, '$lte': endTime}}
        count = collection.count_documents(sql)
        result = collection.find(sql)
        if count > 0:
            for i in result:
                data["time"] = i["date"].strftime('%Y-%m-%d %H:%M:%S')
                sql_p = {'devId': imei, 'time': {"$gte": i["date"]}}
                result_p = collection_p.find(sql_p).sort('time', 1).limit(1)  # 获取休眠取消后第一个定位点时间
                for j in result_p:
                    data["duration"] = self.sleep_time(data["time"], j['time'].strftime('%Y-%m-%d %H:%M:%S'))
                sql_s = {'devId': imei, 'date': {"$gte": i["date"]}}  # 获取休眠取消后第一个状态表的数据
                sql_s2 = {'devId': imei, 'date': {"$lte": i["date"]}}  # 获取休眠前最后第一个状态表的数据
                res_s = collection_s.find(sql_s).limit(1)
                res_s2 = collection_s.find(sql_s2).sort('date', -1).limit(1)
                for k in res_s:
                    # print(k['lithium'])
                    for m in res_s2:
                        data["lit"] = k['lithium'] - m['lithium']
                        l.append(data.copy())
            return l
        else:
            return '暂无数据'

    def Distinguish_lbs_gps(self, imei=None, start_time=None, end_Time=None):
        a = self.find_more_postion(imei, start_time, end_Time)
        l_gps = []
        l_lbs = []
        for index, value in enumerate(a):
            if int(value['type']) == 0:
                l_gps.append(a[index].copy())
            else:
                l_lbs.append(a[index].copy())

        return l_gps, l_lbs

    def find_msg(self, DeviceCode, page=1, size=10, desc=1):
        da = my_sql.get_index_id(DeviceCode, page=1, size=10, desc=1)
        collection = self.db.smsQueue
        data = {
            'start_msg': '',
            'arrive_msg': ''
        }
        l = []
        for i in da:
            s_da = {
                'qtime': '',
                'content': '',
                'msgtype': '',
                'code': ''
            }
            a_da = {
                'qtime': '',
                'content': '',
                'msgtype': '',
                'code': ''
            }

            sql_start = {'code': str(i['id']), 'msgtype': 1}
            # count_end = collection.count_documents(sql_start)
            result_start = collection.find(sql_start).skip((page - 1) * size).limit(size)
            for d in result_start:
                s_da['qtime'] = d['qtime'].strftime('%Y-%m-%d %H:%M:%S')
                s_da['content'] = d['content']
                s_da['msgtype'] = d['msgtype']
                s_da['code'] = d['code']
                data['start_msg'] = s_da
            sql_arrive = {'code': str(i['id']), 'msgtype': 2}
            # count_arrive = collection.count_documents(sql_end)
            result_arrive = collection.find(sql_arrive).skip((page - 1) * size).limit(size)
            for d in result_arrive:
                a_da['qtime'] = d['qtime'].strftime('%Y-%m-%d %H:%M:%S')
                a_da['content'] = d['content']
                a_da['msgtype'] = d['msgtype']
                a_da['code'] = d['code']
                data['start_msg'] = a_da
                data['arrive_msg'] = result_arrive
            l.append(data.copy())
        return l

    def find_msg_by_imei(self, Company_Name=None, Index_PactCode=None):
        start_res_data = {
            "send_time": "",
            "send_location": "",
            "sms_content": "【物流源】{}发给您的物流运单{}已发货，请使用电子回单编号{}或运单号在物流源公众号、微信小程序上查询货物的在途情况。",
            "type": "1"  # startMessage
        }
        l = []
        arriv_res_data = {
            "send_time": "",
            "send_location": "",
            "sms_content": "【物流源】您的物流运单{}来自{}预计将于{}后到达指定收货地址，请知悉。您的签收码是{}，请妥善保管切勿泄露。",
            "type": "2"  # arriveMessage
        }
        collection = self.db.smsQueue
        end_s = Index_PactCode + '.' + Company_Name
        end_sql = {'content': {'$regex': end_s}}
        result_end = collection.find(end_sql)
        start_collection = self.db.startMessage
        arriv_collection = self.db.arriveMessage
        start_s = Company_Name + '.' + Index_PactCode
        start_sql = {'content': {'$regex': start_s}}
        result_start = collection.find(start_sql)
        for i in result_start:
            start_res_data['send_time'] = self.get_location_time(i["qtime"])
            start_collection_sql = {'code': '{}'.format(i['code'])}
            startmsq_res = start_collection.find(start_collection_sql)
            for k in startmsq_res:
                lng = k['lng']
                lat = k['lat']
                start_res_data['send_location'] = self.trans_add(lat, lng)
            msg = i['content'].split('|')
            start_res_data['sms_content'] = start_res_data['sms_content'].format(*msg)
            l.append(start_res_data.copy())
        for i in result_end:
            arriv_res_data['send_time'] = self.get_location_time(i["qtime"])
            start_collection_sql = {'code': '{}'.format(i['code'])}
            startmsq_res = arriv_collection.find(start_collection_sql)
            for k in startmsq_res:
                lng = k['lng']
                lat = k['lat']
                arriv_res_data['send_location'] = self.trans_add(lat, lng)
            msg = i['content'].split('|')
            arriv_res_data['sms_content'] = arriv_res_data['sms_content'].format(*msg)
            l.append(arriv_res_data.copy())
        return l

    def get_location_time(self, t):
        t = t + +datetime.timedelta(hours=8)
        l_t = t.strftime("%Y-%m-%d %H:%M:%S")
        return l_t

    def sleep_time(self, start, end):
        format = '%Y-%m-%d %H:%M:%S'
        a = datetime.datetime.strptime(start, format)
        b = datetime.datetime.strptime(end, format)
        time_all = (b - a).total_seconds()
        m, s = time_all // 60, time_all % 60
        h, m = m // 60, m % 60
        if h > 24:
            d = h // 24
            hh = h % 24
            content = "休眠时长：" + str(d) + "天" + str(hh) + "小时" + str(m) + "分钟" + str(s) + "秒"
        else:
            content = "休眠时长：" + str(h) + "小时" + str(m) + "分钟" + str(s) + "秒"
        return content

    def find_more_sleepNotice(self, imei=None, start_time=None, end_Time=None, size=20, page=1):
        l = []
        data = {
            "time": ""
        }
        collection = self.db.sleepNotice
        startTime = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(end_Time, '%Y-%m-%d %H:%M:%S')
        imei = str(imei)
        sql = {'imei': imei, 'date': {'$gte': startTime, '$lte': endTime}}
        count = collection.count_documents(sql)
        if page > 1:
            result = collection.find(sql).sort('date', -1).limit(size).skip(size * (page - 1))
        else:
            result = collection.find(sql).sort('date', -1).limit(size).skip(size * (page - 1))
        for i in result:
            data['time'] = str(i['date']).split('.')[0]
            l.append(data.copy())
        return l

    def find_last_sleepNotice(self, imei=None):
        l = []
        data = {
            "time": ""
        }
        collection = self.db.sleepNotice
        imei = str(imei)
        sql = {'imei': imei}
        count = collection.count_documents(sql)
        result = collection.find(sql).sort('date', -1).limit(1)
        for i in result:
            data['time'] = str(i['date']).split('.')[0]
            l.append(data.copy())
        return l

    # db_name = 'test'
    def find_one_elc(self, imei=None):
        l = []
        collection = self.db.status
        sql = {'devId': imei}
        result = collection.find(sql).sort('date', -1).limit(1)
        for i in result:
            l.append(i['lithium'])

        return l

    def find_more_elc(self, imei=None, start_time=None, end_Time=None):
        l = []
        startTime = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(end_Time, '%Y-%m-%d %H:%M:%S')
        collection = self.db.status
        sql = {'devId': imei, 'date': {'$gte': startTime, '$lte': endTime}}
        result = collection.find(sql).sort('date', -1)
        for i in result:
            l.append(i['lithium'])
        return l


# db = client[db_name]
# 连接所用集合，也就是我们通常所说的表，position为表名
# db和collection都是延时创建的，在添加Document时才真正创建


'''

select * from TMS_OrderIndex_Sms where Index_PactCode = '2200142892'
select * from TMS_OrderIndex where Index_PactCode = '2200142892' and Index_RootOrderID = Index_ID
db.getCollection('status').find({} 
 sql = {'devId':str(i['Index_DeviceCode']),'time':{'$gte':i['Index_FromTime'],'$lte':i['Index_ToTime']}}
 db.getCollection('smsQueue').find({'content':{$regex:/上海中保物流有限公司\|RLN190122046/}}) 出发
 db.getCollection('smsQueue').find({'content':{$regex:/RLN190122046\|上海中保物流有限公司/}}) 到达
 
'''
# #
my_mog = my_mog()
# data = [
#     {"Company_Name": '上海中保物流有限公司'},
#     {"Index_PactCode": "RLN190122046"}
# ]
# my_mog.find_msg_by_imei(Company_Name = '上海中保物流有限公司',Index_PactCode = "RLN190122046")
# 351608086434002
# a = my_mog.find_more_sleepNotice('351608086029910','2019-11-15 05:05:28','2019-11-21 03:31:23')
# b = my_mog.find_last_sleepNotice('351608086029910')
# a = my_mog.find_sleep('351608086029910','2019-11-15 05:05:28','2019-11-21 03:31:23')
# print(a)
# print(b)
# b = my_mog.sleep_time('2019-11-15 05:05:00','2019-11-16 07:05:00') 
# my_mog.find_last_postion(imei ='351608087081225')
# print(my_mog.find_status(351608087081225))
# print(my_mog.find_more_postion(imei='351608087081225',start_time='2019-04-21 01:11:11',end_Time='2019-05-21 23:59:59'))
# a = my_mog.find_more_postion(imei='351608086050445',start_time='2019-04-21 01:11:11',end_Time='2019-11-21 23:59:59')
# a = my_mog.find_sleep(imei='351608086050445',start_time='2019-04-21 01:11:11',end_Time='2019-11-21 23:59:59')
#
# print(a)
#
# a = my_mog.db_electric('351608085028046')
# print(a)
# db.getCollection('smsQueue').find({'content':{$regex:/上海林内有限公司\|RLN180104023/}})
post_data = {"Company_Name": "荣邦国际物流(上海)有限公司", "Index_PactCode": "8841712020030301"}
my_mog.find_msg_by_imei(**post_data)
