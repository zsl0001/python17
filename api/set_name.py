import sys

import stomp

sys.path.append("..")
from datetime import datetime, timedelta
from time import sleep

from sqlalchemy import or_

from models import db
from my_db.my_models import m_set
import models
from my_db import Models
import requests
import random


class Set_Name:
    def __init__(self, data=None, ip=None):
        if 'datalist' not in data.keys():
            self.Models = Models.OrderResult
            self.m_set = m_set
            self.type = data['type']
            self.ip = ip
            self.Set_Name = data['User_name']
            self.user_id = data['user_id']
            self.page = data['page']
            self.size = data['size']
            self.datalist = []
            self.name = []
        else:
            self.datalist = data['datalist']
            # self.name = data['datalist']['name']
            self.Models = Models.OrderResult
            self.m_set = m_set
            self.type = data['type']
            self.ip = ip
            self.Set_Name = data['username']
            self.user_id = data['user_id']
            self.page = data['page']
            self.size = data['size']

    def set_cp_name(self):
        for i in self.datalist:
            set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            imei = i['imei']
            my_data = {
                'setype': self.type,
                'imei': imei,
                'content': i['name']
            }
            my_data2 = {
                'setype': '4',
                'imei': imei,
                'content': 3600
            }
            url2, tag2 = self.m_set.set_devices(my_data2)
            set_request2 = requests.post(url2)
            add_models = models.ReceiptSetLog()
            url, tag = self.m_set.set_devices(my_data)
            set_request = requests.post(url)
            add_models.Content = url
            add_models.IMEI = imei
            self.name = i['name']
            add_models.Set_Name = self.Set_Name
            add_models.Tag = tag
            add_models.CP_Name = self.name
            add_models.Status_Code = set_request.status_code
            add_models.Set_Time = set_time
            add_models.Set_Type = self.type
            add_models.IP = self.ip
            add_models.User_ID = int(self.user_id)
            db.session.add(add_models)
            db.session.commit()
            db.session.close()
        sleep(60)
        self.check_res()
        self.set_device_result()

    @staticmethod
    def get_location_time(t):
        t = t + +timedelta(hours=8)
        return t

    def check_res(self):
        add_models = models.ReceiptSetLog()
        for i in self.datalist:
            tag = db.session.query(models.ReceiptSetLog).filter(models.ReceiptSetLog.IMEI == i['imei']).order_by(
                models.ReceiptSetLog.Set_Time.desc()).first()
            b = self.Models.objects(tag=int(tag.Tag)).order_by('-time').limit(1)
            if len(b) != 0:
                for k in b:
                    t = self.get_location_time(k.date)
                    if t > datetime.strptime(tag.Set_Time.split('.')[0], "%Y-%m-%d %H:%M:%S"):
                        tag.Result = 1
                    else:
                        tag.Result = 0
            else:
                tag.Result = 0
            db.session.commit()

    def get_set_name_result(self):
        res_data = {
            'imei': '',
            'set_time': '',
            'set_type': '设置屏显',
            'set_content': '',
            'res': '',
        }
        ret_data = {
            'total': '',
            'datalist': ''
        }
        uid = db.session.query(models.User).filter(models.User.id == self.user_id).first().role_id
        # imei = models.ReceiptSetLog.query.with_entities(models.ReceiptSetLog.IMEI).order_by(
        #     models.ReceiptSetLog.IMEI).distinct().paginate(int(self.page),
        #                                                    int(self.size),
        #                                                    False)
        A = db.session.execute(
            "select  IMEI from ERE.dbo.Receipt_Set_Log group by IMEI  order by max(Set_Time) desc offset {} row fetch next {} row only".format(
                (self.page - 1) * self.size, self.size))
        res_list = []
        if uid == 1:
            for i in A:
                a = db.session.query(models.ReceiptSetLog).filter(models.ReceiptSetLog.IMEI == i[0]).order_by(
                    models.ReceiptSetLog.Set_Time.desc()).first()
                res_data['imei'] = i[0]
                res_data['set_content'] = a.CP_Name
                res_data['set_time'] = a.Set_Time.split('.')[0]
                res_data['res'] = a.Result
                res_list.append(res_data.copy())
        ret_data['datalist'] = res_list
        total = db.session.execute("select count(distinct(IMEI)) from ERE.dbo.Receipt_Set_Log")
        for t in total:
            ret_data['total'] = t[0]
        return ret_data

    def set_device_result(self):
        r = db.session.query(models.ReceiptSetLog).filter(models.ReceiptSetLog.Result == 0).order_by(
            models.ReceiptSetLog.Set_Time.desc()).all()
        for i in r:
            b = self.Models.objects(tag=int(i.Tag)).order_by('-time').limit(1)
            if len(b) != 0:
                for k in b:
                    t = self.get_location_time(k.date)
                    if t > datetime.strptime(i.Set_Time.split('.')[0], "%Y-%m-%d %H:%M:%S"):
                        i.Result = 1
                    else:
                        i.Result = 0
            else:
                i.Result = 0
            db.session.commit()

    def send_set_name_cmd(self):

        __topic_name1 = '/queue/SETTING_CMD_SETT'
        # __host = '122.51.209.32'
        __host = '10.81.101.117'
        __port = 61613
        __user = 'admin'
        # __password = 'admin'
        __password = 'nanruan@9.07'
        mq_conn = stomp.Connection10([(__host, __port)], auto_content_length=False)
        mq_conn.connect(__user, __password, wait=True)
        for i in self.datalist:
            add_models = models.ReceiptSetLog()
            set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ran = random.randint(10, 99)  # 生成随机数
            imei = str(i['imei'])
            print(imei)
            tag = imei[-7:] + str(ran)
            order_content = imei + '#' + tag + '#' + i['name'] + '#' + '7'
            mq_conn.send(__topic_name1, order_content)
            add_models.Content = order_content
            add_models.IMEI = imei
            self.name = i['name']
            add_models.Set_Name = self.Set_Name
            add_models.Tag = tag
            add_models.Result = 0
            add_models.CP_Name = self.name
            add_models.Set_Time = set_time
            add_models.Set_Type = self.type
            add_models.IP = self.ip
            add_models.User_ID = int(self.user_id)
            db.session.add(add_models)
            db.session.commit()
            db.session.close()
        sleep(60)
        self.check_res()
        self.set_device_result()

    def aotu_send_cmd(self):
        __topic_name1 = '/queue/SETTING_CMD_SETT'
        __host = '122.51.209.32'
        # __host = '10.81.101.117'
        __port = 61613
        __user = 'admin'
        __password = 'admin'
        # __password = 'nanruan@9.07'
        mq_conn = stomp.Connection10([(__host, __port)], auto_content_length=False)
        mq_conn.connect(__user, __password, wait=True)
        res = models.ReceiptSetLog.query.with_entities(models.ReceiptSetLog.IMEI).distinct().all()
        for i in res:
            re = db.session.query(models.ReceiptSetLog).filter(models.ReceiptSetLog.IMEI == i[0],
                                                               models.ReceiptSetLog.Result == 0).order_by(
                models.ReceiptSetLog.Set_Time.desc()).first()
            # print(re.Content,re.Set_Time)
            if re:
                mq_conn.send(__topic_name1, re.Content)
        sleep(60)
        self.check_res()
        self.set_device_result()
        return '命令执行成功'


def get_ln(patcode, imei):
    res = db.session.query(models.TMSOrderIndex).filter(models.TMSOrderIndex.Index_PactCode == patcode,
                                                        models.TMSOrderIndex.Index_SrcOrderID == 0,
                                                        models.TMSOrderIndex.Index_Status.between(0, 16),
                                                        models.TMSOrderIndex.Index_DeviceCode == imei).first()
    to_laction = res.Index_ToLocation.split(',')[1] + ',' + res.Index_ToLocation.split(',')[0]
    from_laction = res.Index_FromLocation.split(',')[1] + ',' + res.Index_FromLocation.split(',')[0]
    # print(to_laction,from_laction)
    return to_laction, from_laction


def get_ln2(patcode, imei):
    res = db.session.query(models.TMSOrderIndex).filter(models.TMSOrderIndex.Index_PactCode == patcode,
                                                        models.TMSOrderIndex.Index_SrcOrderID == 0,
                                                        models.TMSOrderIndex.Index_Status.between(0, 16),
                                                        models.TMSOrderIndex.Index_DeviceCode == imei).first()
    to_laction = res.Index_ToLocation.split(',')[1] + ',' + res.Index_ToLocation.split(',')[0]
    from_laction = res.Index_FromLocation.split(',')[1] + ',' + res.Index_FromLocation.split(',')[0]
    # print(to_laction,from_laction)
    return to_laction, from_laction, res.Index_From, res.Index_To


# get_ln('m202005270222', '351608086050666')

# data = {"type":"7","User_name":"kf02","user_id":"84","page":1,"size":25,"datalist":[{"imei":"351608086050684","name":"某某公司"},{"imei":"351608086051096","name":"某某二司"}],"id":"84","username":"客服2","useraccount":"kf02"}
# #
# s = Set_Name(data=data, ip='192.168.1.1')
# s.send_set_name_cmd()
# s.aotu_send_cmd()
