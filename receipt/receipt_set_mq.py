# sp_pub_sendmessage
# coding:utf-8
import os
import sys
import time

sys.path.append("..")
from datetime import datetime
import pymssql
from pymongo import MongoClient
from sqlalchemy import create_engine, func, BigInteger, or_

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
# --------------连接数据库需要的类---------------
from sqlalchemy import create_engine  # 建立数据库引擎
from sqlalchemy.orm import sessionmaker  # 建立会话session

Base = declarative_base()  # 实例,创建基类
my_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
download_path = os.path.join(my_path, 'receipt')
imei_path = os.path.join(download_path, 'imei')
imei_list = []
with open(imei_path, 'r') as f:
    for i in f:
        imei_list.append(i.strip('\n'))


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


class TMSDevice(Base):
    __tablename__ = 'TMS_Devices'
    __table_args__ = {'schema': 'WLY.dbo'}
    Device_ID = Column('Device_ID', BigInteger, nullable=False, index=True, primary_key=True)
    Device_IMEICode = Column('Device_IMEICode', nullable=False)
    Device_CompanyID = Column('Device_CompanyID', BigInteger)
    Device_Invalid = Column('Device_Invalid', Integer)
    Device_Type = Column('Device_Type', Integer, nullable=False)


class TMSRegister(Base):
    __tablename__ = 'TMS_Register'
    __table_args__ = {'schema': 'WLY.dbo'}
    id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    index_phone = Column(String(128))
    index_deviceCode = Column(String(128))
    index_insertTime = Column(DateTime, default=datetime.now)
    index_Invalid = Column(Integer, default=0)
    index_creator = Column(String(128))
    index_updateTime = Column(DateTime, default=datetime.now)


class TMSOrderIndex(Base):
    __tablename__ = 'TMS_OrderIndex'
    __table_args__ = {'schema': 'WLY.dbo'}
    Index_ID = Column(BigInteger, primary_key=True)
    opt_status = Column(Integer, nullable=False, )
    Index_Code = Column(String(50), nullable=False)
    Index_PactCode = Column(String(50))
    Index_EndUserID = Column(BigInteger, )
    Index_EndUserName = Column(String(300))
    Index_From = Column(String(300))
    Index_FromProvince = Column(BigInteger, )
    Index_FromCity = Column(BigInteger, )
    Index_FromDistrict = Column(BigInteger, )
    Index_FromTime = Column(DateTime)
    Index_To = Column(String(300))
    Index_ToProvince = Column(BigInteger, )
    Index_ToCity = Column(BigInteger, )
    Index_ToDistrict = Column(BigInteger, )
    Index_ToTime = Column(DateTime)
    Index_TransportMode = Column(BigInteger)
    Index_GoodsCategory = Column(BigInteger)
    Index_PackageMode = Column(BigInteger)
    Index_ChargeMode = Column(BigInteger)
    Index_PriceUnit = Column(BigInteger)
    Index_Status = Column(BigInteger, nullable=False, )
    Index_StatusTime = Column(DateTime, nullable=False)
    Index_SrcOrderID = Column(BigInteger, index=True, )
    Index_RootOrderID = Column(BigInteger, index=True, )
    Index_SrcClass = Column(BigInteger, nullable=False, )
    Index_Kms = Column(BigInteger, )
    Index_CarType = Column(BigInteger, )
    Index_DriverID = Column(BigInteger, )
    Index_CarID = Column(BigInteger, )
    Index_SupplierID = Column(BigInteger, )
    Index_SupplierCompanyID = Column(BigInteger, )
    Index_CustomerID = Column(BigInteger, )
    Index_CustomerCompanyID = Column(BigInteger, )
    Index_ShipMode = Column(BigInteger, )
    Index_Pick = Column(BigInteger, )
    Index_Delivery = Column(BigInteger, )
    Index_Creator = Column(BigInteger, nullable=False, )
    Index_CreatorCompanyID = Column(BigInteger, nullable=False, )
    Index_CreateTime = Column(DateTime, nullable=False, )
    Index_Confirmer = Column(BigInteger, )
    Index_ConfirmTime = Column(DateTime)
    Index_Singer = Column(BigInteger, )
    Index_SignTime = Column(DateTime)
    Index_ReceiptDoc = Column(String(512))
    Index_Exception = Column(String(512), )
    Index_Invalid = Column(Integer, nullable=False, )
    Index_Comments = Column(String(256, 'Chinese_PRC_CI_AS'))
    Index_OnLoad = Column(BigInteger, )
    Index_OffLoad = Column(BigInteger, )
    Index_Insurance = Column(BigInteger, )
    Index_Description = Column(String, )
    Index_Combined = Column(BigInteger, )
    Index_CustomerSymbolID = Column(BigInteger, )
    Index_SupplierSymbolID = Column(BigInteger, )
    Index_ReceiptDoc1 = Column(String(512))
    Index_ReceiptDoc2 = Column(String(512))
    Index_ReceiptDoc3 = Column(String(512))
    Index_FromContact = Column(String(300))
    Index_ToContact = Column(String(300))
    Index_PrevOrderID = Column(BigInteger, )
    Index_DeviceCode = Column(String(50))
    Index_GoodsLst = Column(String)
    Index_RealFromTime = Column(DateTime)
    Index_RealToTime = Column(DateTime)
    Index_ReceiptDoc4 = Column(String(512))
    Index_ReceiptDoc5 = Column(String(512))
    Index_ReceiptDoc6 = Column(String(512))
    Index_ReceiptDoc7 = Column(String(512))
    Index_ReceiptDoc8 = Column(String(512))
    Index_ReceiptDoc9 = Column(String(512))
    Index_FromOperator = Column(String(100))
    Index_TerminalOrderID = Column(BigInteger, )
    Index_TerminalOrderCode = Column(String(100))
    Index_CustomerName = Column(String(300), )
    Index_SupplierName = Column(String(300), )
    Index_CreatorCompanyName = Column(String(300), )
    Index_CustomerSymbolName = Column(String(300), )
    Index_SupplierSymbolName = Column(String(300), )
    Index_BeSplit = Column(Integer, )
    Index_SplitType = Column(Integer, )
    Index_CombinedOrderAmount = Column(BigInteger, )
    Index_CombinedFrom = Column(String(300), )
    Index_CombinedTo = Column(String(300), )
    Index_TCacheReady = Column(Integer, )
    Index_StartMsgTime = Column(DateTime, )
    Index_ArriveMsgTime = Column(DateTime, )
    Index_VerifyCode = Column(String(6, 'Chinese_PRC_CI_AS'), )
    Index_DeviceCreatTime = Column(DateTime, )
    Index_GPSStartTime = Column(DateTime, )
    Index_DeviceBindingTime = Column(DateTime, )
    Index_FromLocation = Column(String(50, 'Chinese_PRC_CI_AS'), )
    Index_ToLocation = Column(String(50, 'Chinese_PRC_CI_AS'), )
    Index_ContainsBillDay = Column(DateTime, )
    Index_TrackType = Column(Integer, )
    Index_Fromtype = Column(Integer, nullable=False, )
    Index_Totype = Column(Integer, nullable=False, )
    Index_RollBack = Column(Integer, nullable=False, )
    Index_CusRollBack = Column(Integer, nullable=False, )
    Index_tpPrint = Column(String(200, 'Chinese_PRC_CI_AS'), )
    Index_GUID = Column(String(50), )
    Index_FromManID = Column(Integer)
    Index_FromMan = Column(String(50))
    Index_ToManID = Column(Integer)
    Index_ToMan = Column(String(50))
    Index_RollBackOrderID = Column(BigInteger, nullable=False, )
    Index_ReceipTime = Column(DateTime)
    Index_ExceptionType = Column(Integer, )
    Index_AssessLevel = Column(Integer, )
    Index_AssessMent = Column(String(200), )
    Index_CloseMark = Column(Integer, )
    Index_CloseMent = Column(String(100), )
    Index_Addorder = Column(Integer, nullable=False, )
    Index_AddPacth = Column(String(200), )
    Index_CarCount = Column(Integer, nullable=False, )
    Index_AutoSchedule = Column(Integer, nullable=False, )
    Index_CombinePrice = Column(Integer, nullable=False, )
    Index_OrderType = Column(Integer, )
    Index_SupplierType = Column(Integer, )
    Index_CloseInitiator = Column(String(100))
    Index_CloseType = Column(BigInteger)
    Index_signinfotype = Column(Integer, )
    Index_signinfo = Column(String)
    Index_RollBckLst = Column(String, )
    Index_VerifySiginTime = Column(DateTime, )
    Index_CreateType = Column(Integer, nullable=False, )
    Index_ReceiptType = Column(Integer)
    Index_additionTransportType = Column(String(1))
    Index_DeviceCode2 = Column(String(255))
    Index_RealFromStatus = Column(Integer)
    Index_WithChildType = Column(Integer)


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

# import stomp
# import time__topic_name1

# 推送到主题
__topic_name1 = '/queue/SETTING_CMD_SETT'
# __host = '122.51.209.32'
__host = '10.81.101.117'
__port = 61613
__user = 'admin'

# __password = 'admin'


__password = 'nanruan@9.07'


# def set_imei():
#     mq_conn = stomp.Connection10([(__host, __port)], auto_content_length=False)
#     # conn.start()
#     mq_conn.connect(__user, __password, wait=True)
#     mq_conn.send(__topic_name1, '351608086050742#100863313#300#4')
#     time.sleep(1)
#     mq_conn.disconnect()


def get_set_data():  # 获取符合条件的订单
    l = []
    m = []
    res = []
    try:
        cur.execute("exec sp_pub_sendmessage")
        result = cur.fetchall()
        for i in result:
            res_regs = session.query(TMSRegister.index_deviceCode).filter(TMSRegister.index_deviceCode == i['IMEICode'],
                                                                          TMSRegister.index_deviceCode == 0).first()  # index_deviceCode index_Invalid
            if res_regs is None:
                l.append({'FromCity': i['FromCity'], 'ToCity': i['ToCity'], 'IMEI': str(i['IMEICode']), 'id': i['Id'],
                          'PactCode': i['PactCode']})
        for k in l:
            m.append(k['IMEI'])
        set_m = list(set(m))
        print(set_m)
        data1 = {'IMEI': '', 'id': '', 'Count': ''}
        data2 = {'IMEI': '', 'id': '', 'Count': ''}
        for d in set_m:  # 2960 大田
            datian = session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == d, TMSDevice.Device_Invalid == 0,
                                                     TMSDevice.Device_Type == 3,TMSDevice.Device_CompanyID != 2960).first()
            s_m = []
            if datian:
                print(d)
                for imei in result:
                    if imei['IMEICode'] == d:
                        # print('------------',d)
                        if imei['FromCity'] == imei['ToCity']:
                            data1['IMEI'] = d
                            data1['id'] = imei['Id']
                            data1['Count'] = 300
                            Count = 300
                        elif imei['Customer'] == '孩子王儿童用品股份有限公司':
                            data1['IMEI'] = d
                            data1['id'] = imei['Id']
                            data1['Count'] = 300
                            Count = 300
                        else:
                            data2['IMEI'] = d
                            data2['id'] = imei['Id']
                            data2['Count'] = 3600
                            Count = 3600
                        s_m.append(Count)
                if min(s_m) == 300:
                    res.append(data1.copy())
                else:
                    res.append(data2.copy())
                print(res)
    except Exception as e:
        print(e)
    print(res)
    return res


#


def up_data_receipt(my_data):  # 将订单更新到数据库
    l = []
    for i in my_data:
        Set_Time = datetime.now()
        b = ReceiptSetInfo()
        a = session.query(ReceiptSetInfo).filter(ReceiptSetInfo.Tag == i['id'])
        if a.first():
            l.append({'imei': a.first().IMEI, 'res': '设备对应的订单已经录入', 'order_id': a.first().Tag})
        else:
            b.IMEI = i['IMEI']
            b.Set_Time = Set_Time
            b.Tag = i['id']
            b.Type = 4
            r = session.query(ReceiptSetInfo).filter(ReceiptSetInfo.IMEI == i['IMEI']).order_by(
                ReceiptSetInfo.Set_Time.desc()).first()
            if r:  # 如果有历史记录
                if int(r.Content) != int(i['Count']):  # 上次设置的值不等于这次的值
                    b.Content = i['Count']
                    try:
                        session.add(b)
                        session.commit()
                        session.close()
                    except Exception as e:
                        print(e)
            else:
                b.Content = i['Count']
                try:
                    session.add(b)
                    session.commit()
                    session.close()
                except Exception as e:
                    print(e)
    print(l)
    return l


def get_no_order_imei():
    res = session.query().with_entities(ReceiptSetInfo.IMEI).distinct().all()
    l = []
    m = []
    for i in res:
        company_id = session.query(TMSDevice).filter(TMSDevice.Device_Invalid == 0,
                                                     TMSDevice.Device_IMEICode == i.IMEI).first()
        if company_id:
            order = session.query(TMSOrderIndex).filter(TMSOrderIndex.Index_DeviceCode == i.IMEI,
                                                        TMSOrderIndex.Index_SrcClass == 1,
                                                        TMSOrderIndex.Index_Status.between(1, 2),
                                                        or_(
                                                            TMSOrderIndex.Index_SupplierCompanyID == company_id.Device_CompanyID,
                                                            TMSOrderIndex.Index_CreatorCompanyID == company_id.Device_CompanyID)).count()
            if order == 0:
                new_ord = session.query(ReceiptSetInfo).filter(ReceiptSetInfo.IMEI == i.IMEI).order_by(
                    ReceiptSetInfo.Set_Time.desc()).first()
                if len(str(new_ord.Tag)) == 9 and str(new_ord.Tag)[-2:] == '18':
                    l.append({'res': '该设备已经存在', 'imei': i.IMEI, 'tag': new_ord.Tag})
                else:
                    m.append(i.IMEI)
                    new_order = ReceiptSetInfo()
                    new_order.Type = new_ord.Type
                    new_order.IMEI = new_ord.IMEI
                    new_order.Tag = int(str(new_ord.Tag) + '18')
                    new_order.Content = 18000
                    try:
                        session.add(new_order)
                        session.commit()
                        session.close()
                    except Exception as e:
                        print(e)
        data = {'false': m,
                'true': l}
        print(data)
    return data


#
# a = get_set_data()
# up_data_receipt(a)
if __name__ == "__main__":
    while 1:
        print('----------正在获取符合条件的订单------------', datetime.now())
        a = get_set_data()
        print('----------正在同步符合条件的订单------------', datetime.now())
        up_data_receipt(a)
        time.sleep(300)
