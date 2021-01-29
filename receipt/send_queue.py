import sys

sys.path.append("..")
import pymssql
import stomp
import time
# sp_pub_sendmessage
from datetime import datetime

import pymssql
from pymongo import MongoClient
from sqlalchemy import create_engine, func

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
# --------------连接数据库需要的类---------------
from sqlalchemy import create_engine  # 建立数据库引擎
from sqlalchemy.orm import sessionmaker  # 建立会话session

Base = declarative_base()  # 实例,创建基类


# 所有的表必须继承于Base
class ReceiptSetInfo(Base):
    __tablename__ = 'Receipt_Set_Info'  # 定义该表在mysql数据库中的实际名称
    __table_args__ = {'schema': 'ERE.dbo'}
    # 定义表的内容
    ID = Column(Integer, primary_key=True)
    IMEI = Column(String(255), nullable=False)
    Content = Column(String(255), nullable=False)
    Type = Column(String(255), nullable=False)
    Result = Column(Integer, default=0)
    Tag = Column(Integer)
    Set_Time = Column(DateTime, default=datetime.now)


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
collection = db.orderResult

# conn = pymssql.connect('192.168.1.200', 'WLY', 'Wly2.techns@907', 'WLY', charset='utf8')
conn = pymssql.connect('172.16.16.23', 'WLY', 'Wly2.techns@907', 'WLY', charset='utf8')
cur = conn.cursor(as_dict=True)
# 推送到主题
__topic_name1 = '/queue/SETTING_CMD_SETT'
# __host = '122.51.209.32'
__host = '10.81.101.117'
__port = 61613
__user = 'admin'

# __password = 'admin'


__password = 'nanruan@9.07'


def send_order(mq_conn):
    res = session.query(ReceiptSetInfo.IMEI, func.max(ReceiptSetInfo.Set_Time)).filter(
        ReceiptSetInfo.Result == 0).group_by(ReceiptSetInfo.IMEI).all()
    for k in res:
        res_d = session.query(ReceiptSetInfo).filter(ReceiptSetInfo.IMEI == k[0],
                                                     ReceiptSetInfo.Set_Time == k[1]).order_by(
            ReceiptSetInfo.Set_Time.desc()).first()
        order_content = str(res_d.IMEI) + '#' + str(res_d.Tag) + '#' + str(res_d.Content) + '#' + '4'
        print(order_content)
        mq_conn.send(__topic_name1, order_content)
        session.query(ReceiptSetInfo).filter(ReceiptSetInfo.IMEI == k[0],
                                             ReceiptSetInfo.Set_Time != k[1], ReceiptSetInfo.Result == 0).delete()
        session.commit()
    session.close()


def check_res():
    res = session.query(ReceiptSetInfo).filter(ReceiptSetInfo.Result == 0).all()
    for i in res:
        d = collection.find({'tag': int(i.Tag)})
        for k in d:
            print(i.Tag, '命令发送成功！', datetime.now())
            if k['res']:
                session.query(ReceiptSetInfo).filter(ReceiptSetInfo.Tag == i.Tag).update({"Result": 1})
                session.commit()


if __name__ == "__main__":
    mq_conn = stomp.Connection10([(__host, __port)], auto_content_length=False)
    mq_conn.connect(__user, __password, wait=True)
    print('----------正在确定发送指定------------', datetime.now())
    check_res()
    print('----------正在发送设置指定------------', datetime.now())
    send_order(mq_conn=mq_conn)
    mq_conn.disconnect()
    print('发送完成')
