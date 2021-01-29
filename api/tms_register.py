import math
import os
import re
import sys
import datetime

sys.path.append("..")
from api.bind_company import Set_Device_Comapy
from models import db, TMSDevice, TMSCompany,TemperatureReceipt
from myconfig import my_sql
from sqlalchemy import create_engine, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker  # 建立会话db.session
from sqlalchemy.orm import Query


# engine = create_engine(
#     'mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8'.format(my_sql['username'], my_sql['password'], my_sql['host'],
#                                                            my_sql['db']))
# Base = declarative_base()


# class TMSRegister(Base):
#     __tablename__ = 'TMS_Register'
#     # __table_args__ = {'schema': 'WLY.dbo'}
#     id = Column(BigInteger, nullable=False, index=True, primary_key=True)
#     index_phone = Column(String(128))
#     index_deviceCode = Column(String(128))
#     index_insertTime = Column(DateTime, default=datetime.datetime.now())
#     index_Invalid = Column(Integer, default=0)
#     index_creator = Column(String(128))
#     index_updateTime = Column(DateTime, default=datetime.datetime.now())
class TMSRegister(db.Model):
    __tablename__ = 'TMS_Register'
    __table_args__ = {'schema': 'WLY.dbo'}
    id = db.Column(db.BigInteger, nullable=False, index=True, primary_key=True)
    index_phone = db.Column(db.String(128))
    index_deviceCode = db.Column(db.String(128))
    index_insertTime = db.Column(db.DateTime, default=datetime.datetime.now)
    index_Invalid = db.Column(db.Integer, default=0)
    index_creator = db.Column(db.String(128))
    index_updateTime = db.Column(db.DateTime, default=datetime.datetime.now)


def get_register_devices_list(data):
    # Sesssion = db.sessionmaker(bind=engine)  # 产生会话
    # db.session = Sesssion()  # 创建db.session实例
    page = data['page']
    size = data['size']
    res = db.session.query(TMSRegister).filter(TMSRegister.index_Invalid == 0)
    if 'index_phone' in data.keys():
        res = res.filter(TMSRegister.index_phone == data['index_phone'])
    if 'deviceCode' in data.keys():
        res = res.filter(TMSRegister.index_deviceCode == data['deviceCode'])
    res = res.order_by(TMSRegister.index_insertTime.desc())
    all_res = res.limit(size).offset((page - 1) * size).all()
    rs_data = {
        'total_page': math.ceil(res.count() / size),
        'datalist': '',
        'total': res.count()
    }
    l = []
    for i in all_res:  # index_phone index_deviceCode index_insertTime index_Invalid index_creator
        l.append(
            {'deviceCode': i.index_deviceCode, 'index_phone': i.index_phone,
             'index_insertTime': str(i.index_insertTime).split('.')[0],
             'index_Invalid': i.index_Invalid, 'index_creator': i.index_creator})
    rs_data['datalist'] = l
    return rs_data


# data = {'size': 25, 'page': 1, id: "84", 'username': "超级管理员", 'useraccount': "admin"}

# a = get_register_devices_list({'page': 1, 'size': 25})
# print(a)

#  {"data_list":[{"index_deviceCode":"351608086050300","index_phone":"18677775555"}],
#  "id":"84","username":"超级管理员","useraccount":"admin"}
# [{"type":3,"simid":3,"imeicodes":"","simbatch":"","phoneNo":"","timer":"","expiryStarttime":"","expiryEndtime":"","companyID":31454,"companyName":"蕾雅","comments":"","salerName":"","imeicode":"351608086000001",
# "user_name":"admin","id":"84","company_code":"ORG0072233279","useraccount":"admin","username":"超级管理员"}]
def add_register_devices(data):
    # Sesssion = db.sessionmaker(bind=engine)  # 产生会话00000\#    db.session = Sesssion()  # 创建db.session实例
    # db.session = Sesssion()  # 创建db.session实例
    tms_register_obj = TMSRegister()
    error_list = []
    for i in data['data_list']:
        tms_register_obj.index_creator = data['username']
        device_data = db.session.query(TMSDevice.Device_IMEICode).filter(
            TMSDevice.Device_IMEICode == i['index_deviceCode'], TMSDevice.Device_Invalid == 0).first()
        if device_data:
            error_list.append({'res': '设备已经绑定', 'code': -10001, 'index_deviceCode': i['index_deviceCode']})
        else:
            if re.match(r'1[3,4,5,7,8]\d{9}', i['index_phone']):
                tms_register_obj.index_phone = i['index_phone']
            else:
                tms_register_obj.index_phone = ' '
                error_list.append({'res': '电话号码格式错误', 'code': -10001, 'index_phone': i['index_phone']})
            if str(i['index_deviceCode']).startswith('351608086'):
                tms_register_obj.index_deviceCode = i['index_deviceCode']
            else:
                tms_register_obj.index_deviceCode = ' '
                error_list.append({'res': '电子回单格式错误', 'code': -10001, 'index_deviceCode': i['index_deviceCode']})
            res = db.session.query(TMSRegister).filter(TMSRegister.index_Invalid == 0,
                                                       TMSRegister.index_deviceCode == i['index_deviceCode']).first()
            if res:
                tms_register_obj.index_deviceCode = ' '
                tms_register_obj.index_phone = ' '
                error_list.append({'res': '设备录入重复，请先禁用', 'code': -10001, 'index_deviceCode': i['index_deviceCode']})
            if tms_register_obj.index_deviceCode == ' ' and tms_register_obj.index_phone == ' ':
                continue
            else:
                add_devices = TMSDevice()
                add_devices.Device_InsertTime = datetime.datetime.now()
                tmp = db.session.query(TemperatureReceipt.imei).filter(TemperatureReceipt.imei==i['index_deviceCode']).first()
                if tmp:
                    add_devices.Device_temperature = 1
                else:
                    add_devices.Device_temperature = 0
                add_devices.Device_Type = 3
                add_devices.Device_OwnerType = 0
                add_devices.Device_Invalid = 0
                add_devices.Device_SIMid = 3
                add_devices.Device_IMSI = ' '
                add_devices.Device_Creator = ' '
                add_devices.Device_IMEICode = i['index_deviceCode']
                company_id_list = db.session.query(TMSCompany.Company_ID).filter(
                    TMSCompany.Company_Phone == i['index_phone'], TMSCompany.Company_Invalid == 0,
                    TMSCompany.Company_Personal == 3).first()
                if company_id_list:
                    company_id = company_id_list[0]
                    add_devices.Device_CompanyID = company_id
                else:
                    error_list.append({'res': '手机号未授权登录，无法绑定', 'code': -10001})
                try:
                    db.session.add(tms_register_obj)
                    db.session.add(add_devices)
                    db.session.commit()
                except Exception as e:
                    print(e)
    if error_list:
        return error_list
    else:
        return {'res': '添加成功', 'code': 10001}


# dat = {"data_list": [{"index_deviceCode": "351608086050303", "index_phone": "18680160654"}], "id": "84",
#        "username": "超级管理员", "useraccount": "admin"}
# a = add_register_devices(dat)
# print(a)


def set_register_devices_status(data):
    # Sesssion = db.sessionmaker(bind=engine)  # 产生会话
    # db.session = Sesssion()  # 创建db.session实例
    index_deviceCode = data['index_deviceCode']
    index_Invalid = data['index_Invalid']
    res = db.session.query(TMSRegister.index_Invalid).filter(TMSRegister.index_deviceCode == index_deviceCode)
    res_D = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode ==index_deviceCode).first()
    if res:
        res.update({"index_Invalid": index_Invalid})
        res_D.Device_Invalid = index_Invalid
        try:
            db.session.commit()
        except Exception as e:
            print(e)
        return {'res': '修改成功', 'code': 10001}
    else:
        return {'res': '设备不存在', 'code': 10001}
