# sp_pub_sendmessage
# coding:utf-8
import os
import sys

sys.path.append("..")
import datetime
import pymongo
from pymongo import MongoClient
from sqlalchemy import create_engine, func, BigInteger, or_

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
# --------------连接数据库需要的类---------------
from sqlalchemy import create_engine  # 建立数据库引擎
from sqlalchemy.orm import sessionmaker  # 建立会话session

Base = declarative_base()  # 实例,创建基类
my_path = os.path.abspath(os.curdir)
imei_path = os.path.join(my_path, 'imei')
imei_list = []
with open(imei_path, 'r') as f:
    for i in f:
        imei_list.append(i.strip('\n'))


# 所有的表必须继承于Base
class ReceiptTemp(Base):
    __tablename__ = 'Receipt_Temp'  # 定义该表在mysql数据库中的实际名称
    __table_args__ = {'schema': 'ERE.dbo'}
    # 定义表的内容
    id = Column(Integer, primary_key=True)
    imei = Column(String(255), nullable=False)
    res = Column(Integer, default=0)
    last_hbt_time = Column(DateTime)
    setting_time = Column(DateTime)


# db_connect_string = 'mssql+pymssql://WLY:Wly2.techns@907@192.168.1.200:1433/ERE?charset=utf8'
db_connect_string = 'mssql+pymssql://WLY:Wly2.techns@907@172.16.16.23:1433/ERE?charset=utf8'
# 以mysql数据库为例：mysql+数据库驱动：//用户名：密码@localhost:3306/数据库
engine = create_engine(db_connect_string)  # 创建引擎
Sesssion = sessionmaker(bind=engine)  # 产生会话
session = Sesssion()  # 创建Session实例

# M_conn = MongoClient('192.168.1.168', 27017)

M_conn = MongoClient(
    host='mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
db = M_conn.er
collection = db.status

import stomp
import time

# 推送到主题
__topic_name1 = '/queue/SETTING_CMD_ORD'
# __host = '122.51.209.32'
__host = '10.81.101.117'
__port = 61613
__user = 'admin'

# __password = 'admin'


__password = 'nanruan@9.07'


def set_imei(imei):
    mq_conn = stomp.Connection10([(__host, __port)], auto_content_length=False)
    mq_conn.connect(__user, __password, wait=True)
    mq_conn.send(__topic_name1, '{}#20200831#3'.format(imei))
    try:
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        return {'res': "更新失败!", "code": -205}
        # 6.响应结果
    return {'res': "更新成功!", "code": 200}
    mq_conn.disconnect()


def get_location_time(t):
    a_t = t + datetime.timedelta(hours=8)
    l_t = a_t.strftime("%Y-%m-%d %H:%M:%S")
    return l_t


#
# for i in imei_list:
#     a = set_imei(i)
#     print(a)


def check():
    for k in imei_list:
        time.sleep(1)
        print('正在处理IMEI码为{}的设备！'.format(k))
        res = session.query(ReceiptTemp).filter(ReceiptTemp.imei == k).first()
        t = datetime.datetime.now()
        res.setting_time = t
        # set_time = datetime.datetime.strptime(res.setting_time.split('.')[0], '%Y-%m-
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        d = collection.find({'devId': str(k)}).sort('date', -1).limit(1)
        for i in d:
            lt = get_location_time(i['date'])
            now = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
            p_time = datetime.datetime.strptime(lt, '%Y-%m-%d %H:%M:%S')
            res.last_hbt_time = p_time
            a = (now - p_time).seconds
            print('最后心跳时间{},当前时间为{},相差{}秒!'.format(p_time, now, a))
            # if a <= 300:
            set_imei(k)
        try:
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()


#
while 1:
    check()
    print('处理完成')
    time.sleep(1800)
