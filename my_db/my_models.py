import sys

sys.path.append("..")
import datetime
import mongoengine
import models
from my_db import Models
import random
import requests


class My_Models:
    def __init__(self):
        self.base_url = "http://139.196.160.63:1222/"
        self.tag = random.randint(100000000, 999999999)  # 生成随机数

    @staticmethod
    def get_location_time(t):
        t = t + +datetime.timedelta(hours=8)
        return t

    def get_alarm_imei_info(self, data):

        dat = {
            'Device_Status': '',
            'lithium': -1,
            'gsmLevel': -1,
            'charging': -1,
            'temperature': 'null',
        }
        l = []
        for i in data:
            b = datetime.datetime.now()
            if list(i['Device_IMEICode'])[8] == '6':
                st = Models.Status.objects(devId=str(i['Device_IMEICode'])).order_by('-devId').limit(1)
                if len(st) != 0:
                    for j in st:
                        dat['lithium'] = j.lithium
                        dat['gsmLevel'] = j.gsmLevel
                        dat['charging'] = j.charging
                        dat['temperature'] = j.temperature
                        if (b - self.get_location_time(j.date)).total_seconds() > 420:
                            d_data = Models.SleepNotice.objects(imei=str(j.devId)).limit(1)
                            if len(d_data) != 0:
                                for m in d_data:
                                    if m.date > j.date:
                                        dat['Device_Status'] = '休眠'
                                    else:
                                        dat['Device_Status'] = '离线'
                            else:
                                dat['Device_Status'] = '离线'
                        else:
                            dat['Device_Status'] = '在线'
                else:
                    dat['Device_Status'] = '离线'
                    dat['Device_Status'] = '离线'
                    dat['lithium'] = '-1'
                    dat['gsmLevel'] = '-1'
                    dat['charging'] = '-1'
                    dat['temperature'] = 'null'
                i = {**i, **dat}
                l.append(i.copy())
            elif list(i['Device_IMEICode'])[8] == '7':
                st = Models.Log.objects(imei=str(i['Device_IMEICode'])).order_by('-imei').limit(1)
                if len(st) != 0:
                    for j in st:
                        dat['lithium'] = str(j.content).split(',')[-1]
                        dat['gsmLevel'] = str(j.content).split(',')[1]
                        if (b - self.get_location_time(j.time)).total_seconds() > 420:
                            d_data = Models.SleepNotice.objects(imei=str(j.imei)).limit(1)
                            if len(d_data) != 0:
                                for m in d_data:
                                    if m.date > j.date:
                                        dat['Device_Status'] = '休眠'
                                    else:
                                        dat['Device_Status'] = '离线'
                            else:
                                dat['Device_Status'] = '离线'
                        else:
                            dat['Device_Status'] = '在线'
                else:
                    dat['Device_Status'] = '离线'
                    dat['lithium'] = '-1'
                    dat['gsmLevel'] = '-1'
                    dat['charging'] = '-1'
                    dat['temperature'] = 'null'
                i = {**i, **dat}
                l.append(i.copy())
        return l

    def get_3imei_info(self, page, size, data):
        # data = models.get_company_id_and_name(page, size)
        dat = {
            'Device_Status': '',
            'lithium': -1,
            'gsmLevel': -1,
            'charging': -1,
            'temperature': 'null',
        }
        l = []
        dd = {
            "count": "",
            "list": ""
        }
        for i in data:
            b = datetime.datetime.now()
            if i['Device_IMEICode'][8] == '6':
                st = Models.Status.objects(devId=str(i['Device_IMEICode'])).order_by('-devId').limit(1)
                if len(st) != 0:
                    for j in st:
                        dat['lithium'] = j.lithium
                        dat['gsmLevel'] = j.gsmLevel
                        dat['charging'] = j.charging
                        dat['temperature'] = j.temperature
                        if (b - self.get_location_time(j.date)).total_seconds() > 420:
                            d = Models.SleepNotice.objects(imei=str(j.devId)).limit(1)
                            if len(d) != 0:
                                for m in d:
                                    if m.date > j.date:
                                        dat['Device_Status'] = '休眠'
                                    else:
                                        dat['Device_Status'] = '离线'
                            else:
                                dat['Device_Status'] = '离线'
                        else:
                            dat['Device_Status'] = '在线'
                else:
                    dat['Device_Status'] = '离线'
                    dat['lithium'] = '-1'
                    dat['gsmLevel'] = '-1'
                    dat['charging'] = '-1'
                    dat['temperature'] = 'null'
                i = {**i, **dat}
                l.append(i.copy())
            elif i['Device_IMEICode'][8] == '7':
                st = Models.Log.objects(imei=str(i['Device_IMEICode'])).order_by('-imei').limit(1)
                if len(st) != 0:
                    for j in st:
                        dat['lithium'] = str(j.content).split(',')[-1]
                        dat['gsmLevel'] = str(j.content).split(',')[1]
                        if (b - self.get_location_time(j.time)).total_seconds() > 420:

                            d = Models.SleepNotice.objects(imei=str(j.imei)).limit(1)
                            if len(d) != 0:
                                for m in d:

                                    if m.date > j.date:

                                        dat['Device_Status'] = '休眠'
                                    else:

                                        dat['Device_Status'] = '离线'
                            else:
                                dat['Device_Status'] = '离线'
                        else:

                            dat['Device_Status'] = '在线'
                else:
                    dat['Device_Status'] = '离线'

                i = {**i, **dat}
                l.append(i.copy())
                i.clear()
        dd["list"] = l
        # dd["count"] = len(l)
        return dd

    #
    def get_alarm(self, data):
        data = self.get_alarm_imei_info(data)
        l = []
        d = {
            'count': '',
            'list': ''
        }
        for i in data:
            if i['Device_Status'] == '离线' and int(i['lithium']) != 0:
                l.append(i.copy())
            elif i['Device_Status'] == '休眠' and int(i['lithium']) < 20:
                l.append(i.copy())
        d['count'] = len(l)
        d['list'] = l
        return d

    def get_alarm2(self, data):
        d = {'count': '', 'list': ''}
        dat = {
            'Device_Status': '',
            'lithium': -1,
            'gsmLevel': -1,
            'charging': -1,
            'temperature': 'null',
        }
        l = []
        for i in data:
            b = datetime.datetime.now()
            if list(i['Device_IMEICode'])[8] == '6':
                st = Models.Status.objects(devId=str(i['Device_IMEICode'])).order_by('-devId').limit(1)
                if len(st) != 0:
                    for j in st:
                        dat['lithium'] = j.lithium
                        dat['gsmLevel'] = j.gsmLevel
                        dat['charging'] = j.charging
                        dat['temperature'] = j.temperature
                        if (b - self.get_location_time(j.date)).total_seconds() > 420:
                            d_data = Models.SleepNotice.objects(imei=str(j.devId)).limit(1)
                            if len(d_data) != 0:
                                for m in d_data:
                                    if m.date > j.date:
                                        dat['Device_Status'] = '休眠'
                                    else:
                                        dat['Device_Status'] = '离线'
                            else:
                                dat['Device_Status'] = '离线'
                        else:
                            dat['Device_Status'] = '在线'
                else:
                    dat['Device_Status'] = '离线'
                    dat['Device_Status'] = '离线'
                    dat['lithium'] = '-1'
                    dat['gsmLevel'] = '-1'
                    dat['charging'] = '-1'
                    dat['temperature'] = 'null'
                i = {**i, **dat}
                l.append(i.copy())
        d['count'] = len(l)
        d['list'] = l
        return d

    def add_data(self, data=None):  # 字段包括 User_ID Name Content IP Tag Time
        db = models.db
        # m = models.Order_List.query.filter().all()
        log = models.Order_List(**data)
        db.session.add(log)
        db.session.commit()

    def set_devices(self, data=None):
        tag = random.randint(100000000, 2999999999)  # 生成随机数
        # tag = self.tag
        set_url = "setting/charge/"
        imei = data['imei']
        setype = data['setype']
        content = data['content']
        if setype in ['1', '3', '4', '5', '7'] and len(
                imei) == 15:  # {1、WorkMode ；2、AddrInfo ；3、Time2Sleep ；4、PosInvl ；5、HbInvl；6、imei 7/公司名字
            if setype == '1':  # 设置工作模式 0表示智能，1表示定时
                if content in ['0', '1']:
                    url = str(self.base_url) + set_url + str(imei) + '/' + str(setype) + '/' + str(content) + '/' + str(
                        tag)
                else:
                    return '参数错误'
            elif setype == '3':  # 设置休眠间隔 大于等于180s
                if int(content) >= 180:
                    url = str(self.base_url) + set_url + str(imei) + '/' + str(setype) + '/' + str(content) + '/' + str(
                        tag)
                else:
                    return '参数错误'
            elif setype == '4':  # 设置定时间隔 大于15S
                if int(content) >= 180:
                    url = str(self.base_url) + set_url + str(imei) + '/' + str(setype) + '/' + str(content) + '/' + str(
                        tag)
                else:
                    return '参数错误'
            elif setype == '5':  # 设置心跳间隔 大约15s 小于120s
                if 15 < int(content) < 120:
                    url = str(self.base_url) + set_url + str(imei) + '/' + str(setype) + '/' + str(content) + '/' + str(
                        tag)
                else:
                    return '参数错误'
            elif setype == '7':  # 设置公司名字，英文8个字符，中文4个中文
                if len(content.encode('gbk')) <= 8:
                    url = str(self.base_url) + set_url + str(imei) + '/' + str(setype) + '/' + str(content) + '/' + str(
                        tag)
                else:
                    return '参数错误'
            return url, tag
        else:
            return '参数错误'

    def sys_devices(self, data=None):  # 服务器指令
        # tag = random.randint(100000000, 999999999)  # 生成随机数
        tag = self.tag
        set_url = "order/charge/"
        imei = data['imei']
        setype = data['setype']
        if setype in ['1', '2', '3'] and len(imei) == 15:  # （1，position；2，updatesys；3，reset）
            url = str(self.base_url) + set_url + str(imei) + '/' + str(setype) + '/' + str(tag)
            return url
        else:
            return '参数错误'

    def search_devices(self, data=None):  # 服务器指令
        # tag = random.randint(100000000, 999999999)  # 生成随机数
        tag = self.tag
        set_url = "inquire/select/"
        imei = data['imei']
        url = str(self.base_url) + set_url + str(imei) + '/' + str(tag)
        return url

    def send_set_devices(self, data=None):
        url = self.set_devices(data)
        tag = self.tag
        re = requests.get(url)
        print(url)
        print(re.content)
        return url

    @staticmethod
    def check_set_devices_order(data=None):
        dat = Models.OrderResult.objects.filter(mongoengine.Q(devId=data['imei']) & mongoengine.Q(tag=826667935))
        for i in dat:
            print(i.devId)
        pass


m_set = My_Models()

# imei = data['imei']
# setype = data['setype']
# content = data['content']
# data ={
#     "imei":'351608086050742',
#     "setype":'7',
#     "content":'湖南测试',
# }

# url,tag = m_set.set_devices(data)
# print(url,tag)
