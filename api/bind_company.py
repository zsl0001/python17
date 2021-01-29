import os
import sys
from time import strftime

import pandas as pd
import pymssql

sys.path.append("..")
from models import db, TMSDevice, TMSCompany, TMSSale, StockLog, User, TMSOrderIndex, ReceiptLog,TemperatureReceipt
from datetime import datetime, timedelta
from myconfig import mgdb, sqldb, api_cfg
from math import *

my_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
download_path = os.path.join(my_path, 'download')


class ReceiptCompanyLog(db.Model):
    __tablename__ = 'Receipt_Company_Log'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    New_Company = db.Column(db.String(128))
    Device_IMEI = db.Column(db.String(128))
    Original_Company = db.Column(db.String(128))
    InsertTime = db.Column(db.DateTime, default=datetime.now)
    Creator_Name = db.Column(db.String(128))
    Start_Time = db.Column(db.DateTime)
    End_Time = db.Column(db.DateTime)


class TMSMSymbol(db.Model):
    __tablename__ = 'TMS_MSymbol'
    __bind_key__ = 'WLY'
    __table_args__ = {'schema': 'ERE.dbo'}
    Symbol_ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    Symbol_CompanyID = db.Column(db.BigInteger)
    Symbol_Type = db.Column(db.BigInteger)
    Symbol_Code = db.Column(db.String(128))
    Symbol_Name = db.Column(db.String(128))
    Symbol_Invalid = db.Column(db.BigInteger)


class File_Export(db.Model):
    __tablename__ = 'File_Export'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    File_Name = db.Column(db.String(128))
    Creator_Name = db.Column(db.String(128))
    Creator_Time = db.Column(db.DateTime, default=datetime.now)
    Download = db.Column(db.BigInteger)


def Receipt_Company_Log(Device_IMEI, InsertTime, Creator_Name, New_Company, Start_Time='', End_Time='',
                        Original_Company=None):  # 设备分配记录
    log = ReceiptCompanyLog()
    log.Device_IMEI = Device_IMEI
    log.Creator_Name = Creator_Name
    log.New_Company = New_Company
    log.Original_Company = Original_Company
    log.InsertTime = InsertTime
    if Start_Time:
        log.Start_Time = Start_Time
    if End_Time:
        log.End_Time = End_Time
    try:
        db.session.add(log)
        db.session.commit()
        return {'res': '修改成功!', 'code': 1001}
    except Exception as e:
        print(e)
        return {'res': '修改失败!', 'code': -1001}


def Receipt_Log(IMEI, User_Name, User_ID, Set_Time, IP, Content):  # 设备操作日志
    log = ReceiptLog()
    log.IMEI = IMEI
    log.User_Name = User_Name
    log.User_ID = User_ID
    log.InsertTime = Set_Time
    log.IP = IP
    log.Content = Content
    try:
        db.session.add(log)
        db.session.commit()
        return {'res': '修改成功!', 'code': 1001}
    except Exception as e:
        print(e)
        return {'res': '修改失败!', 'code': -1001}


def get_my_device_excel():
    res = db.session.query(TMSDevice.Device_IMEICode, TMSDevice.Device_PhoneNo, TMSDevice.Device_SIMid,
                           TMSDevice.Device_IMSI, TMSDevice.Device_OwnerType, TMSDevice.Device_Type,
                           TMSDevice.Device_temperature, TMSCompany.Company_Name, TMSDevice.Device_Invalid).filter(
        TMSDevice.Device_CompanyID == TMSCompany.Company_ID).order_by(TMSDevice.Device_InsertTime.desc())
    l = []  # SIMid 1 长沙移动 2 浙江移动 3 湖南物联网协会
    for i in res.all():
        my_order = db.session.query(TMSOrderIndex.Index_SupplierName, TMSOrderIndex.Index_CreateTime).filter(
            TMSOrderIndex.Index_DeviceCode == i[0], TMSDevice.Device_Invalid == 0,
            TMSOrderIndex.Index_SrcClass == 2).order_by(TMSOrderIndex.Index_CreateTime.desc()).first()
        if my_order:
            lastSupName = my_order[0]
            lastBindTime = my_order[1]
        else:
            '''('351608086021818', '1440500307606', 1, ' ', 0, 3, 0, '拓领环球物流(中国)有限公司增城分公司')'''
            lastSupName = ' '
            lastBindTime = ' '
        k = list(i)
        if k[2] == 1:
            k[2] = '长沙移动'
        elif k[2] == 2:
            k[2] = '浙江移动'
        elif k[2] == 3:
            k[2] = '湖南物联网协会'
        if k[4] == 0:  # 自有 租用
            k[4] = '自有'
        elif k[4] == 1:
            k[4] = '租用'
        if k[5] == 1:  # 1 2 3代
            k[5] = '1代'
        elif k[5] == 2:
            k[5] = '2代'
        elif k[5] == 3:
            k[5] = '3代'
        if k[6] == 0:  # 温控
            k[6] = '否'
        elif k[6] == 1:
            k[6] = '是'
        if k[8] == 0:  # 禁用
            k[8] = '否'
        elif k[8] == 1:
            k[8] = '是'
        k.append(lastSupName)
        k.append(lastBindTime)
        l.append(tuple(k))
    return l


class Set_Device_Comapy:
    def __init__(self, ip, data=None):
        self.data = data
        self.ip = ip
        my_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
        self.download_path = os.path.join(my_path, 'download')

    def get_all_Device(self):
        '''{"ownerType":"","imsi":"","type":"","companyName":"","imeicode":"","phoneNo":"","invalid":0}'''
        page = self.data['page']
        size = self.data['size']
        if 'invalid' in self.data.keys():
            invalid = [self.data['invalid']]
        else:
            invalid = [0, 1]
        res = db.session.query(TMSDevice, TMSCompany).filter(
            TMSDevice.Device_CompanyID == TMSCompany.Company_ID,
            TMSDevice.Device_Invalid.in_(invalid)).order_by(
            TMSDevice.Device_InsertTime.desc())
        if 'ownerType' in self.data.keys():
            ownerType = self.data['ownerType']
            if len(str(ownerType)) >= 1:
                res = res.filter(TMSDevice.Device_OwnerType == ownerType)
        if 'imsi' in self.data.keys():
            imsi = self.data['imsi']
            if len(imsi) >= 1:
                res = res.filter(TMSDevice.Device_IMSI.like('%' + str(imsi) + '%'))
        if 'type' in self.data.keys():
            type = self.data['type']
            if len(str(type)) >= 1:
                res = res.filter(TMSDevice.Device_Type == type)
        if 'companyName' in self.data.keys():
            companyName = self.data['companyName']
            if len(companyName) >= 1:
                cp_l = []
                CompanyID = db.session.query(TMSCompany.Company_ID).filter(
                    TMSCompany.Company_Name.like('%' + str(companyName) + '%'), TMSCompany.Company_Invalid == 0,
                                                                                TMSCompany.Company_Status == 2).all()
                for k in CompanyID:
                    cp_l.append(k[0])
                res = res.filter(TMSDevice.Device_CompanyID.in_(cp_l))
        if 'imeicode' in self.data.keys():
            imeicode = self.data['imeicode']
            if len(imeicode) >= 1:
                res = res.filter(TMSDevice.Device_IMEICode.like('%' + str(imeicode) + '%'))
        if 'phoneNo' in self.data.keys():
            phoneNo = self.data['phoneNo']
            if len(phoneNo) >= 1:
                res = res.filter(TMSDevice.Device_PhoneNo.like('%' + str(phoneNo) + '%'))
        if 'invalid' in self.data.keys():
            invalid = self.data['invalid']
            if len(str(invalid)) >= 1:
                res = res.filter(TMSDevice.Device_Invalid == invalid)
        if 'company_personal' in self.data.keys():
            company_personal = self.data['company_personal']
            res = res.filter(TMSCompany.Company_Personal == company_personal)
        if 'temperature' in self.data.keys():
            temperature = self.data['temperature']
            if len(str(temperature)) >= 1:
                res = res.filter(TMSDevice.Device_temperature == int(temperature))
        res = res.paginate(int(page), int(size), False)
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            # my_order = db.session.query(TMSOrderIndex).filter(
            #     TMSOrderIndex.Index_DeviceCode == i.TMSDevice.Device_IMEICode,
            #     TMSOrderIndex.Index_Status.between(2, 16),
            #     TMSOrderIndex.Index_SrcClass == 2).order_by(TMSOrderIndex.Index_CreateTime.desc()).first()
            #
            # if my_order:
            #     lastSupName = my_order.Index_SupplierName
            #     lastBindTime = my_order.Index_CreateTime
            #     print(my_order.Index_SupplierName, my_order.Index_CreateTime)
            # else:
            #     lastBindTime = ''
            l.append({'imeicode': i.TMSDevice.Device_IMEICode, 'phoneNo': i.TMSDevice.Device_PhoneNo,
                      'simid': i.TMSDevice.Device_SIMid, 'insertTime': str(i.TMSDevice.Device_InsertTime).split('.')[0],
                      'invalid': i.TMSDevice.Device_Invalid, 'type': i.TMSDevice.Device_Type,
                      'companyName': i.TMSCompany.Company_Name, 'imsi': i.TMSDevice.Device_IMSI,
                      'companyID': i.TMSCompany.Company_ID, 'ownerType': i.TMSDevice.Device_OwnerType,
                      # 'lastSupName': lastSupName, 'lastBindTime': str(lastBindTime).split('.')[0],
                      'Device_SIMBatch': i.TMSDevice.Device_SIMBatch, 'temperature': i.TMSDevice.Device_temperature,
                      'Company_Personal': i.TMSCompany.Company_Personal,
                      'expiry_starttime': str(i.TMSDevice.Device_Expiry_Starttime),
                      'expiry_endtime': str(i.TMSDevice.Device_Expiry_Endtime)
                      })
        rs_data['datalist'] = l
        return rs_data

    def add_devices(self):
        l_error = []
        for i in self.data:
            useraccount = i['useraccount']
            username = i['username']
            device = TMSDevice()
            res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == i['imeicode'],
                                                     TMSDevice.Device_Invalid == 0).first()
            if res:
                l_error.append({'imei': i['imeicode'], 'res': '新增失败，设备已存在!', 'code': -10001})
            else:
                res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == i['imeicode'],
                                                         TMSDevice.Device_Invalid == 1).first()
                if res:
                    device = res
                set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cp_name = db.session.query(TMSCompany).filter(TMSCompany.Company_ClientCode == i['company_code'],
                                                              TMSCompany.Company_Status == 2,
                                                              TMSCompany.Company_Invalid == 0).first()
                if cp_name:
                    # user_name = db.session.query(User).filter(User.id == i['id'], User.is_disable == 0).first()
                    # user_name = user_name.sales_name
                    content = f"{username}将设备编码为{i['imeicode']}的设备,分配给了{cp_name.Company_Name},修改时间为{set_time},修改地ip为{self.ip}."
                    Receipt_Log(IMEI=i['imeicode'], User_Name=username, User_ID=i['id'],
                                Set_Time=set_time, IP=self.ip, Content=content)
                    device.Device_Type = i['type']
                    device.Device_SIMid = i['simid']
                    device.Device_IMEICode = i['imeicode']
                    device.Device_CompanyID = cp_name.Company_ID
                    res = db.session.query(TemperatureReceipt).filter(TemperatureReceipt.imei == i['imeicode']).count()
                    if res:
                        temperature = 1
                    else:
                        temperature = 0
                    device.Device_temperature = temperature
                    device.Device_InsertTime = set_time
                    device.Device_Expiry_Starttime = ''
                    device.Device_Expiry_Endtime = ''
                    device.Device_IMSI = ''
                    device.Device_Creator = i['id']
                    device.Device_OwnerType = 0
                    device.Device_Invalid = 0
                    if 'simbatch' in i.keys() and len(str(i['simbatch'])) >= 1:
                        device.Device_SIMBatch = i['simbatch']
                    if 'phoneNo' in i.keys() and len(str(i['phoneNo'])) >= 1:
                        device.Device_PhoneNo = i['phoneNo']
                    if 'expiryStarttime' in i.keys() and 'expiryEndtime' in i.keys():
                        if len(str(i['expiryStarttime'])) > 1 and len(str(i['expiryEndtime'])) >= 1:
                            device.Device_Expiry_Starttime = i['expiryStarttime']
                            device.Device_Expiry_Endtime = i['expiryEndtime']
                            device.Device_OwnerType = 1
                    if 'salerName' in i.keys() and len(str(i['salerName'])) >= 1:
                        device.Device_SalerName = i['salerName']
                    if 'comments' in i.keys() and len(str(i['comments'])) >= 1:
                        device.Device_Comments = i['comments']
                    # if 'comments' in i.keys() and len(i['comments']:
                    #     device.Device_Comments = i['comments']
                    Receipt_Company_Log(Device_IMEI=i['imeicode'], New_Company=cp_name.Company_Name,
                                        InsertTime=set_time,
                                        Creator_Name=username, Start_Time=device.Device_Expiry_Starttime,
                                        End_Time=device.Device_Expiry_Endtime)
                    try:
                        db.session.add(device)
                        db.session.commit()
                        # return {'res': '修改成功!', 'code': 1001}
                    except Exception as e:
                        print(e)
                        l_error.append({'res': '修改失败!', 'code': -10001, 'imei': i['imeicode']})
                else:
                    l_error.append({'res': '输入的公司编码错误，公司不存在!', 'imei': i['imeicode'], 'code': -10001})
        rs_data = {
            'code': -10001,
            'datalist': l_error
        }
        if len(l_error):
            return rs_data
        else:
            return {'res': '新增成功!', 'code': 1001}

    def device_check(self):
        imei = self.data['imeicode']
        res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == imei,
                                                 TMSDevice.Device_Invalid == 0).first()
        if res:
            return {'res': '设备已存在!', 'code': -1001}
        else:
            return {'res': '设备可以添加!', 'code': 1001}

    def get_all_company_name(self):
        print(self.data)
        page = self.data['page']
        size = self.data['size']
        if 'company_name' in self.data.keys():
            company_name = '%' + self.data['company_name'] + '%'
        else:
            company_name = '%%'
        res = db.session.query(TMSCompany.Company_Name, TMSCompany.Company_ID, TMSCompany.Company_ClientCode,
                               TMSCompany.Company_Personal).filter(
            TMSCompany.Company_Name.like(company_name),
            TMSCompany.Company_Status == 2,
            TMSCompany.Company_Invalid == 0).order_by(
            TMSCompany.Company_InsertTime.desc()).paginate(int(page), int(size), False)
        l = []
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        if res:
            for i in res.items:
                l.append(
                    {'Company_Name': i[0], 'Company_ID': i[1], 'Company_ClientCode': i[2], 'Company_Personal': i[3]})
        else:
            return {'res': '暂无数据!', 'code': 1001}
        rs_data['datalist'] = l
        return rs_data

    def set_devices_status(self):
        error_list = []
        for i in self.data:
            useraccount = i['useraccount']
            username = i['username']
            res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == i['imeicode'],
                                                     TMSDevice.Device_Invalid == 0).first()
            invalid = i['invalid']
            if int(invalid) not in [0, 1]:
                error_list.append({'imei': i['imeicode'], 'res': '参数错误，修改失败！', 'code': -100001})
            if res is None:
                error_list.append({'imei': i['imeicode'], 'res': '设备不存在或者已被禁用，请核实后再试！', 'code': -100001})
            else:
                order_status = db.session.query(TMSOrderIndex).filter(TMSOrderIndex.Index_Status == 2,
                                                                      TMSOrderIndex.Index_DeviceCode == i[
                                                                          'imeicode']).count()
                if order_status:
                    error_list.append({'res': '设备绑定的订单未全部签收，请全部签收后再进行操作！', 'imei': i['imeicode'], 'code': -10001})
                else:
                    res.Device_Invalid = invalid
                    # user_name = db.session.query(User).filter(User.id == i['id'], User.is_disable == 0).first()
                    # user_name = user_name.sales_name
                    set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if int(invalid) == 1:
                        content = f"{username}将设备编码为{i['imeicode']}的设备禁用了,修改时间为{set_time},修改地ip为{self.ip}."
                    if int(invalid) == 0:
                        content = f"{username}将设备编码为{i['imeicode']}的设备启用了,修改时间为{set_time},修改地ip为{self.ip}."
                    Receipt_Log(IMEI=i['imeicode'], User_Name=username, User_ID=i['id'], Set_Time=set_time,
                                IP=self.ip,
                                Content=content)
                    try:
                        db.session.add(res)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        return {'res': '修改失败!', 'code': -1001}
        if error_list:
            res_data = {'code': -1001, 'datalist': error_list}
            return res_data
        else:
            return {'code': 1001, 'res': '修改成功！'}

    def get_receipt_company_log(self):
        page = self.data['page']
        size = self.data['size']
        res = db.session.query(ReceiptCompanyLog).filter(
            ReceiptCompanyLog.Device_IMEI == self.data['imeicode']).order_by(
            ReceiptCompanyLog.InsertTime.desc())
        res = res.paginate(int(page), int(size), False)
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            if str(i.Start_Time).split('.')[0]:
                start_time = str(i.Start_Time).split('.')[0]
            else:
                start_time = ' '
            if str(i.End_Time).split('.')[0]:
                end_time = str(i.End_Time).split('.')[0]

            else:
                end_time = ''
            l.append(
                {'imei': i.Device_IMEI, 'company_name': i.New_Company, 'start_time': start_time,
                 'end_time': end_time,
                 'name': i.Creator_Name})
        rs_data['datalist'] = l
        return rs_data

    def get_receipt_Log(self):
        page = self.data['page']
        size = self.data['size']
        res = db.session.query(ReceiptLog).filter(ReceiptLog.IMEI == self.data['imeicode']).order_by(
            ReceiptLog.Set_Time.desc())
        res = res.paginate(int(page), int(size), False)
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            l.append({'content': i.Content, 'name': i.User_Name, 'set_time': str(i.Set_Time).split('.')[0]})
        rs_data['datalist'] = l
        return rs_data

    def batch_disable(self):  # 批量禁用
        cp_error_list = []
        imei_error_list = []
        for i in self.data:
            useraccount = i['useraccount']
            username = i['username']
            cp_id = db.session.query(TMSCompany).filter(TMSCompany.Company_Name == i['company_name'],
                                                        TMSCompany.Company_Invalid == 0,
                                                        TMSCompany.Company_Status == 2,
                                                        TMSCompany.Company_Invalid == 0,
                                                        ).first()
            if cp_id:
                res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == i['imei'],
                                                         TMSDevice.Device_Invalid == 0,
                                                         TMSDevice.Device_CompanyID == cp_id.Company_ID).first()
                if res:
                    order_status = db.session.query(TMSOrderIndex).filter(TMSOrderIndex.Index_Status == 2,
                                                                          TMSOrderIndex.Index_DeviceCode == i[
                                                                              'imei']).count()
                    if order_status:
                        imei_error_list.append(
                            {'res': '设备绑定的订单未全部签收，请全部签收后再进行操作！', 'imei': i['imei'], 'code': -10001})
                    else:
                        set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        res.Device_Invalid = 1
                        # user_name = db.session.query(User).filter(User.id == i['id'], User.is_disable == 0).first()
                        # user_name = user_name.sales_name
                        content = f"{username}将设备编码为{i['imei']}的设备禁用了,修改时间为{set_time},修改地ip为{self.ip}."
                        Receipt_Log(IMEI=i['imei'], User_Name=username, User_ID=i['id'],
                                    Set_Time=set_time, IP=self.ip, Content=content)
                        try:
                            db.session.add(res)
                            db.session.commit()
                        except Exception as e:
                            print(e)
                            imei_error_list.append({'res': '设备已经禁用，请勿重复禁用！', 'imei': i['imei'], 'code': -10001})
                else:
                    imei_error_list.append({'res': '设备不属于该公司！', 'imei': i['imei'], 'code': -10001})
            else:
                cp_error_list.append({'res': '公司不存在！', 'imei': i['imei'], 'code': -10001})
            my_list = imei_error_list + cp_error_list
        if my_list:
            data = {'code': -10001, 'datalist': my_list}
            return data
        else:
            return {'code': 10001, 'res': '修改成功！'}

    def change_imsi(self):  # 修改IMSI码 Device_IMSI
        error_list = []
        for i in self.data:
            useraccount = i['useraccount']
            username = i['username']
            if len(i['imeicode']) != 15 or len(i['imsi']) != 13:
                error_list.append({'res': '参数错误！', 'imei': i['imeicode']})
            else:
                res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == i['imeicode'],
                                                         TMSDevice.Device_Invalid == 0).first()
                if res:
                    set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    res.Device_IMSI = i['imsi']
                    # user_name = db.session.query(User).filter(User.id == i['id'], User.is_disable == 0).first()
                    # user_name = user_name.sales_name
                    content = f"{username}将设备编码为{i['imeicode']}的IMSI修改为{i['imsi']},修改时间为{set_time},修改地ip为{self.ip}."
                    Receipt_Log(IMEI=i['imeicode'], User_Name=username, User_ID=i['id'],
                                Set_Time=set_time, IP=self.ip, Content=content)
                    try:
                        db.session.add(res)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        return {'res': '修改失败!', 'code': -1001}
                else:
                    error_list.append({'res': '设备不存在!', 'imei': i['imeicode'], 'code': -10001})
        if error_list:
            data = {'code': -10001, 'datalist': error_list}
            return data
        else:
            return {'res': '修改成功!', 'code': 1001}

    def change_owner_type(self):
        ip = self.ip
        imei_error_list = []
        for i in self.data:
            useraccount = i['useraccount']
            username = i['username']
            if 'company_name' in i.keys():
                cp_id = db.session.query(TMSCompany).filter(TMSCompany.Company_Name == i['company_name'],
                                                            TMSCompany.Company_Invalid == 0,
                                                            TMSCompany.Company_Status == 2,
                                                            TMSCompany.Company_Invalid == 0,
                                                            ).first()
            else:
                cp_id = db.session.query(TMSCompany).filter(TMSCompany.Company_ID == i['company_id'],
                                                            TMSCompany.Company_Invalid == 0,
                                                            TMSCompany.Company_Status == 2,
                                                            TMSCompany.Company_Invalid == 0,
                                                            ).first()
            if cp_id:
                res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == i['imeicode'],
                                                         TMSDevice.Device_Invalid == 0,
                                                         TMSDevice.Device_CompanyID == cp_id.Company_ID).first()
                if res:
                    set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    res.Device_OwnerType = 0
                    # user_name = db.session.query(User).filter(User.id == i['id'],
                    #                                           User.is_disable == 0).first()
                    # user_name = user_name.sales_name
                    content = f"{username}将设备编码为{i['imeicode']}的设备从租用改成了自有,修改时间为{set_time},修改地ip为{self.ip}."
                    Receipt_Log(IMEI=i['imeicode'], User_Name=username, User_ID=i['id'],
                                Set_Time=set_time, IP=self.ip, Content=content)
                    try:
                        db.session.add(res)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        imei_error_list.append({'res': '参数错误！', 'imei': i['imeicode'], 'code': -10001})
                else:
                    imei_error_list.append({'res': '设备不属于该公司！', 'imei': i['imeicode'], 'code': -10001})
            else:
                imei_error_list.append({'res': '公司不存在！', 'imei': i['imeicode'], 'code': -10001})
        if imei_error_list:
            res_data = {'code': -10001, 'datalist': imei_error_list}
            return res_data
        else:
            return {'code': 1001, 'res': '修改成功！'}

    def excel_test(self):
        my_file_name = self.data['file_name']
        username = sqldb['username']
        password = sqldb['password']
        database = sqldb['database']
        host = sqldb['host']
        conn = pymssql.connect(host, username, password, database)
        # conn = pymssql.connect('192.168.1.200', 'WLY', 'Wly2.techns@907', 'WLY')

        sql2 = '''select i.Index_DeviceCode as '设备编码', i.Index_CreateTime as '最后绑定时间',i.Index_SupplierName as '最后承运商' from TMS_OrderIndex i ,TMS_Devices t  where t.Device_IMEICode = i.Index_DeviceCode and LEN(i.Index_SupplierID )>=1
                  and i.Index_SrcClass =2
                  and LEN(i.Index_SupplierName )>=1
                  order by i.Index_CreateTime desc '''
        df = pd.read_sql(sql=sql2, con=conn)
        # print(df)
        finnal_df = df.iloc[df.groupby(['设备编码']).apply(
            lambda x: x['最后绑定时间'].idxmax())]
        sql3 = '''select
                    d.Device_IMEICode as '设备编码',
                    d.Device_PhoneNo as '设备号码',
                    d.Device_SIMid as 'SIM提供商',
                    d.Device_IMSI as 'IMSI码',
                    d.Device_OwnerType as '是否租用',
                    d.Device_Type as '设备类型',
                    d.Device_temperature as '是否温控',
                    d.Device_Invalid as '是否禁用' ,
                    c.Company_Name as '客户名称'
                    from TMS_Devices d,TMS_Company c where 
                    d.Device_CompanyID = c.Company_ID 
                    and d.Device_Invalid =0
               '''
        if 'ownerType' in self.data.keys():
            d_type = f"and d.Device_OwnerType={self.data['ownerType']}"
        if 'temperature' in self.data.keys():
            d_type = f"and d.Device_temperature={self.data['temperature']}"
        if 'companyName' in self.data.keys():
            name = self.data['companyName']
            sql = f"(SELECT Company_ID from TMS_Company where Company_Name like '%{name}%' and Company_Invalid = 0 and Company_Status =2)"
            d_type = f"and d.Device_CompanyID in {sql}"
        if 'imeicode' in self.data.keys():
            s = "%" + f"{self.data['imeicode']}" + "%"
            d_type = "and d.Device_IMEICode like " + s
        if 'phoneNo' in self.data.keys():
            s = "%" + f"{self.data['phoneNo']}" + "%"
            d_type = "and d.Device_PhoneNo like " + s
        if 'imsi' in self.data.keys():
            s = "%" + f"{self.data['imsi']}" + "%"
            d_type = "and d.Device_IMSI like " + s
        if d_type:
            sql3 = sql3 + d_type
        df2 = pd.read_sql(sql=sql3, con=conn)
        df2.loc[df2['SIM提供商'] == 1, 'SIM提供商'] = '长沙移动'
        df2.loc[df2['SIM提供商'] == 2, 'SIM提供商'] = '浙江移动'
        df2.loc[df2['SIM提供商'] == 3, 'SIM提供商'] = '湖南物联网协会'
        df2.loc[df2['是否租用'] == 1, '是否租用'] = '是'
        df2.loc[df2['是否租用'] == 0, '是否租用'] = '否'
        df2.loc[df2['设备类型'] == 1, '设备类型'] = '1代'
        df2.loc[df2['设备类型'] == 2, '设备类型'] = '2代'
        df2.loc[df2['设备类型'] == 3, '设备类型'] = '3代'
        df2.loc[df2['是否温控'] == 1, '是否温控'] = '是'
        df2.loc[df2['是否温控'] == 0, '是否温控'] = '否'
        df2.loc[df2['是否禁用'] == 1, '是否禁用'] = '是'
        df2.loc[df2['是否禁用'] == 0, '是否禁用'] = '否'
        a = pd.merge(finnal_df, df2, on='设备编码', how='inner')
        b = pd.merge(df2, a, on='设备编码', how='left', suffixes=('', '_y'))
        b.drop(b.filter(regex='_y$').columns.tolist(), axis=1, inplace=True)
        download_path = self.download_path + f'\{my_file_name}'
        b.to_excel(download_path)  # 筛选后的数据生成excel
        return download_path

    def excel_ctrl(self):
        excel_list = os.listdir(self.download_path)
        if len(excel_list) <= 10:
            self.excel_test()
        else:
            return {'res': '最多只能保存10个文件，请删除多余文件后重试！', 'code': -10001}

    def get_all_excel_list(self):  # 获取当前导出文件列表
        res = db.session.query(File_Export).filter().all()
        l = []
        for i in res:
            l.append({'file_name':i.File_Name,'creator_name':i.Creator_Name,'creator_time':str(i.Creator_Time).split('.')[0],'dowload':i.DownLoad})
        return l

    def remove_excel(self):
        file_name = self.data['file_name']
        rm_file_path = os.path.join(my_path, file_name)
        try:
            os.remove(rm_file_path)
        except Exception as e:
            print(e)
            return {'res': '删除失败，请联系管理员处理！', 'code': -10001}

    def close_conn(self):
        db.session.close()

    def get_all_Device22(self):
        '''{"ownerType":"","imsi":"","type":"","companyName":"","imeicode":"","phoneNo":"","invalid":0}'''
        page = self.data['page']
        size = self.data['size']
        # 子查询
        my_l = []
        s1 = ''
        s2 = ''
        sql = '''SELECT 
                        d.Device_IMEICode,
                        d.Device_PhoneNo,
                        d.Device_SIMid,
                        d.Device_InsertTime,
                        d.Device_Invalid,
                        d.Device_Type,
                        d.Device_IMSI,
                        d.Device_OwnerType,
                        d.Device_SIMBatch,
                        d.Device_temperature,
                        d.Device_Expiry_Starttime,
                        d.Device_Expiry_Endtime,
                        c.Company_Name,
                        c.Company_Personal,
                        c.Company_ID,
                        t.Index_CreateTime,
                        t.Index_SupplierName                 
                        from  ({}) as d_id  left outer join TMS_Devices  as d on  d_id.Device_ID = d.Device_ID left outer join (select Index_DeviceCode,max(Index_CreateTime) as Index_CreateTime,max(Index_SupplierName) as Index_SupplierName
                        from TMS_OrderIndex 
                        where LEN(Index_SupplierName)>=2 and Index_TrackType =1 GROUP BY Index_DeviceCode) as t on t.Index_DeviceCode =  d.Device_IMEICode left outer join TMS_Company as c on c.Company_ID = d.Device_CompanyID  where 1 = 1 {} {} ORDER BY d.Device_InsertTime desc offset {} row fetch next {} row only'''
        sql_count = '''
                    SELECT 
                        count(*) as count
                        from  ({}) as d_id  left outer join TMS_Devices  as d on  d_id.Device_ID = d.Device_ID left outer join (select Index_DeviceCode,max(Index_CreateTime) as Index_CreateTime,max(Index_SupplierName) as Index_SupplierName
                        from TMS_OrderIndex 
                        where LEN(Index_SupplierName)>=2 and Index_TrackType =1 GROUP BY Index_DeviceCode) as t on t.Index_DeviceCode =  d.Device_IMEICode left outer join TMS_Company as c on c.Company_ID = d.Device_CompanyID  where 1 = 1 {} {} '''
        sql1 = 'select Device_ID from TMS_Devices where 1=1 '
        if 'invalid' in self.data.keys():
            my_l.append(self.data['invalid'])
            my_l = tuple(my_l)[0]
            s3 = "and Device_Invalid in (" + f"{my_l}" + ')'
        else:
            my_l = (0, 1)
            s3 = f"and Device_Invalid in {my_l}"
        if 'ownerType' in self.data.keys():
            ownerType = self.data['ownerType']
            if len(str(ownerType)) >= 1:
                sql1 = sql1 + f' and Device_OwnerType = {ownerType} '
        if 'imsi' in self.data.keys():
            imsi = self.data['imsi']
            if len(imsi) >= 1:
                sql1 = sql1 + f'and Device_IMSI = {imsi} '
        if 'type' in self.data.keys():
            type = self.data['type']
            if len(str(type)) >= 1:
                sql1 = sql1 + f'and Device_Type = {type} '
        if 'imeicode' in self.data.keys():
            imeicode = self.data['imeicode']
            if len(imeicode) >= 1:
                sql1 = sql1 + f"and Device_IMEICode like '%{imeicode}%'"
        if 'phoneNo' in self.data.keys():
            phoneNo = self.data['phoneNo']
            if len(phoneNo) >= 1:
                sql1 = sql1 + f"and Device_PhoneNo like '%{phoneNo}%' "
        if 'temperature' in self.data.keys():
            temperature = self.data['temperature']
            if len(str(temperature)) >= 1:
                sql1 = sql1 + f"and Device_temperature = {temperature} "
        if 'company_personal' in self.data.keys():
            company_personal = self.data['company_personal']
            s1 = f'and c.Company_Personal ={company_personal}'
        if 'companyName' in self.data.keys():
            companyName = self.data['companyName']
            if len(companyName) >= 1:
                s2 = f"and c.Company_Name like '%{companyName}%' and c.Company_Status = 2 and c.Company_Invalid = 0"

        sql1 = sql1 + s3
        sql = sql.format(sql1, s1, s2, (page - 1) * size, size)
        sql_count = sql_count.format(sql1, s1, s2)
        # print(sql_count)
        cursor = db.session.execute(sql)
        result = cursor.fetchall()
        s_count = db.session.execute(sql_count)
        s_count = s_count.fetchall()
        rs_data = {
            'total_page': ceil(s_count[0][0] / int(size)),
            'datalist': '',
            'total': s_count[0][0]
        }
        l = []
        for i in result:
            if (str(i[15]).split('.')[0]) == 'None':
                bindtime = ' '
            l.append({'imeicode': i[0], 'phoneNo': i[1],
                      'simid': i[2], 'insertTime': str(i[3]).split('.')[0],
                      'invalid': i[4], 'type': i[5],
                      'companyName': i[12], 'imsi': i[6],
                      'company_personal': i[13],
                      'companyID': i[14], 'ownerType': i[7],
                      # 'lastSupName': i[16], 'lastBindTime': bindtime,
                      'Device_SIMBatch': i[8], 'temperature': i[9],
                      'expiry_starttime': str(i[10]),
                      'expiry_endtime': str(i[11])
                      })
        rs_data['datalist'] = l
        return rs_data

    def get_all_count(self):
        '''{"ownerType":"","imsi":"","type":"","companyName":"","imeicode":"","phoneNo":"","invalid":0}'''
        page = self.data['page']
        size = self.data['size']
        # 子查询
        my_l = []
        s1 = ''
        s2 = ''
        sql_count = '''
                    SELECT 
                        count(*) as count
                        from  ({}) as d_id  left outer join TMS_Devices  as d on  d_id.Device_ID = d.Device_ID left outer join (select Index_DeviceCode,max(Index_CreateTime) as Index_CreateTime,max(Index_SupplierName) as Index_SupplierName
                        from TMS_OrderIndex 
                        where LEN(Index_SupplierName)>=2 and Index_TrackType =1 GROUP BY Index_DeviceCode) as t on t.Index_DeviceCode =  d.Device_IMEICode left outer join TMS_Company as c on c.Company_ID = d.Device_CompanyID  where 1 = 1 {} {} '''
        sql1 = 'select Device_ID from TMS_Devices where 1=1 '
        if 'invalid' in self.data.keys():
            my_l.append(self.data['invalid'])
            my_l = tuple(my_l)[0]
            s3 = "and Device_Invalid in (" + f"{my_l}" + ')'
        else:
            my_l = (0, 1)
            s3 = f"and Device_Invalid in {my_l}"
        if 'ownerType' in self.data.keys():
            ownerType = self.data['ownerType']
            if len(str(ownerType)) >= 1:
                sql1 = sql1 + f' and Device_OwnerType = {ownerType} '
        if 'imsi' in self.data.keys():
            imsi = self.data['imsi']
            if len(imsi) >= 1:
                sql1 = sql1 + f'and Device_IMSI = {imsi} '
        if 'type' in self.data.keys():
            type = self.data['type']
            if len(str(type)) >= 1:
                sql1 = sql1 + f'and Device_Type = {type} '
        if 'imeicode' in self.data.keys():
            imeicode = self.data['imeicode']
            if len(imeicode) >= 1:
                sql1 = sql1 + f"and Device_IMEICode like '%{imeicode}%'"
        if 'phoneNo' in self.data.keys():
            phoneNo = self.data['phoneNo']
            if len(phoneNo) >= 1:
                sql1 = sql1 + f"and Device_PhoneNo like '%{phoneNo}%' "
        if 'temperature' in self.data.keys():
            temperature = self.data['temperature']
            if len(str(temperature)) >= 1:
                sql1 = sql1 + f"and Device_temperature = {temperature} "
        if 'company_personal' in self.data.keys():
            company_personal = self.data['company_personal']
            s1 = f'and c.Company_Personal ={company_personal}'
        if 'companyName' in self.data.keys():
            companyName = self.data['companyName']
            if len(companyName) >= 1:
                s2 = f"and c.Company_Name like '%{companyName}%' and c.Company_Status = 2 and c.Company_Invalid = 0"
        sql1 = sql1 + s3
        sql_count = sql_count.format(sql1, s1, s2)
        # print(sql_count)
        s_count = db.session.execute(sql_count)
        s_count = s_count.fetchall()
        rs_data = {
            'total_page': ceil(s_count[0][0] / int(size)),
            'datalist': '',
            'total': s_count[0][0]
        }
        return rs_data

    def get_all_device_excel(self):
        file_export = File_Export()
        my_file_name = self.data['file_name']
        download_path = self.download_path + f'\{my_file_name}'
        '''{"ownerType":"","imsi":"","type":"","companyName":"","imeicode":"","phoneNo":"","invalid":0}'''
        page = self.data['page']
        size = self.data['size']
        if 'invalid' in self.data.keys():
            invalid = [self.data['invalid']]
        else:
            invalid = [0, 1]
        res = db.session.query(TMSDevice, TMSCompany).filter(
            TMSDevice.Device_CompanyID == TMSCompany.Company_ID,
            TMSDevice.Device_Invalid.in_(invalid)).order_by(
            TMSDevice.Device_InsertTime.desc())
        if 'ownerType' in self.data.keys():
            ownerType = self.data['ownerType']
            if len(str(ownerType)) >= 1:
                res = res.filter(TMSDevice.Device_OwnerType == ownerType)
        if 'imsi' in self.data.keys():
            imsi = self.data['imsi']
            if len(imsi) >= 1:
                res = res.filter(TMSDevice.Device_IMSI.like('%' + str(imsi) + '%'))
        if 'type' in self.data.keys():
            type = self.data['type']
            if len(str(type)) >= 1:
                res = res.filter(TMSDevice.Device_Type == type)
        if 'companyName' in self.data.keys():
            companyName = self.data['companyName']
            if len(companyName) >= 1:
                cp_l = []
                CompanyID = db.session.query(TMSCompany.Company_ID).filter(
                    TMSCompany.Company_Name.like('%' + str(companyName) + '%'), TMSCompany.Company_Invalid == 0,
                                                                                TMSCompany.Company_Status == 2).all()
                for k in CompanyID:
                    cp_l.append(k[0])
                res = res.filter(TMSDevice.Device_CompanyID.in_(cp_l))
        if 'imeicode' in self.data.keys():
            imeicode = self.data['imeicode']
            if len(imeicode) >= 1:
                res = res.filter(TMSDevice.Device_IMEICode.like('%' + str(imeicode) + '%'))
        if 'phoneNo' in self.data.keys():
            phoneNo = self.data['phoneNo']
            if len(phoneNo) >= 1:
                res = res.filter(TMSDevice.Device_PhoneNo.like('%' + str(phoneNo) + '%'))
        if 'invalid' in self.data.keys():
            invalid = self.data['invalid']
            if len(str(invalid)) >= 1:
                res = res.filter(TMSDevice.Device_Invalid == invalid)
        if 'company_personal' in self.data.keys():
            company_personal = self.data['company_personal']
            res = res.filter(TMSCompany.Company_Personal == company_personal)
        if 'temperature' in self.data.keys():
            temperature = self.data['temperature']
            if len(str(temperature)) >= 1:
                res = res.filter(TMSDevice.Device_temperature == int(temperature))
        res = res.statement
        df2 = pd.read_sql(res, db.session.bind)
        columns_list = ['设备编码', '设备号码',
                        'SIM提供商', 'IMSI码',
                        '是否租用', '设备类型',
                        '是否温控', '是否禁用',
                        '客户名称', '租用开始时间',
                        '租用结束时间']

        df2.rename(columns={'Device_IMEICode': '设备编码', 'Device_PhoneNo': '设备号码',
                            'Device_SIMid': 'SIM提供商', 'Device_IMSI': 'IMSI码', 'Device_OwnerType': '是否租用',
                            'Device_Type': '设备类型', 'Device_temperature': '是否温控', 'Device_Invalid': '是否禁用',
                            'Company_Name': '客户名称', 'Device_Expiry_Starttime': '租用开始时间',
                            'Device_Expiry_Endtime': '租用结束时间'
                            }, inplace=True)
        df2.loc[df2['SIM提供商'] == 1, 'SIM提供商'] = '长沙移动'
        df2.loc[df2['SIM提供商'] == 2, 'SIM提供商'] = '浙江移动'
        df2.loc[df2['SIM提供商'] == 3, 'SIM提供商'] = '湖南物联网协会'
        df2.loc[df2['是否租用'] == 1, '是否租用'] = '是'
        df2.loc[df2['是否租用'] == 0, '是否租用'] = '否'
        df2.loc[df2['设备类型'] == 1, '设备类型'] = '1代'
        df2.loc[df2['设备类型'] == 2, '设备类型'] = '2代'
        df2.loc[df2['设备类型'] == 3, '设备类型'] = '3代'
        df2.loc[df2['是否温控'] == 1, '是否温控'] = '是'
        df2.loc[df2['是否温控'] == 0, '是否温控'] = '否'
        df2.loc[df2['是否禁用'] == 1, '是否禁用'] = '是'
        df2.loc[df2['是否禁用'] == 0, '是否禁用'] = '否'
        b = df2[columns_list]
        b.to_excel(download_path)
        file_export.Creator_Name = self.data['useraccount']
        file_export.File_Name = self.data['file_name']

        try:
            db.session.add(file_export)
            db.session.commit()
            return {'res': '导出成功!', 'code': 1001}
        except Exception as e:
            print(e)
            return {'res': '导出失败!', 'code': -1001}

    def disabled_devices(self):
        error_list = []
        for i in self.data:
            useraccount = i['useraccount']
            username = i['username']
            res = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == i['imeicode'],
                                                     TMSDevice.Device_Invalid == 0).first()
            invalid = i['invalid']
            if int(invalid) not in [0, 1]:
                error_list.append({'imei': i['imeicode'], 'res': '参数错误，修改失败！', 'code': -100001})
            if res is None:
                error_list.append({'imei': i['imeicode'], 'res': '设备不存在或者已被禁用，请核实后再试！', 'code': -100001})
            else:
                res.Device_Invalid = invalid
                # user_name = db.session.query(User).filter(User.id == i['id'], User.is_disable == 0).first()
                # user_name = user_name.sales_name
                set_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if int(invalid) == 1:
                    content = f"{username}将设备编码为{i['imeicode']}的设备禁用了,修改时间为{set_time},修改地ip为{self.ip}."
                if int(invalid) == 0:
                    content = f"{username}将设备编码为{i['imeicode']}的设备启用了,修改时间为{set_time},修改地ip为{self.ip}."
                Receipt_Log(IMEI=i['imeicode'], User_Name=username, User_ID=i['id'], Set_Time=set_time,
                            IP=self.ip,
                            Content=content)
                try:
                    db.session.add(res)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    return {'res': '修改失败!', 'code': -1001}
        if error_list:
            res_data = {'code': -1001, 'datalist': error_list}
            return res_data
        else:
            return {'code': 1001, 'res': '修改成功！'}

#
# data = {'page': 1, 'size': 25, 'invalid': 0, 'file_name': '10066.xls','useraccount':'admin'}
# c = Set_Device_Comapy(data=data, ip='192.168.1.1')
# b = c.get_all_excel_list()
# d = c.get_all_device_excel()
# print(d)
# print(len(b['datalist']))

# imgpath = os.path.join('silder_img')
# print(download_path + r'\112312312')
# conn = pymssql.connect('192.168.1.200', 'WLY', 'Wly2.techns@907', 'WLY')
# cursor = conn.cursor()
# name = '上海'
# sql1 = f" like '%{name}%'"
# sql = "SELECT Company_ID from TMS_Company where Company_Name" + sql1
# sql2 = "SELECT Company_ID from TMS_Company where Company_Name like '%上海%'"
# cursor.execute(sql)
# res =cursor.fetchall()
# datalist = []
# for s in res:
#     datalist.append(s[0])
# print(datalist)
# my_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
# download_path = os.path.join(my_path, 'download')
# def excel_test():
#     my_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
#     download_path = os.path.join(my_path, 'download')
#     my_file_name = 'test10087.xls'
#     username = sqldb['username']
#     password = sqldb['password']
#     database = sqldb['database']
#     host = sqldb['host']
#     # conn = pymssql.connect(host, username, password, database)
#     conn = pymssql.connect('192.168.1.200', 'WLY', 'Wly2.techns@907', 'WLY')
#
#     sql2 = '''select i.Index_DeviceCode as '设备编码', i.Index_CreateTime as '最后绑定时间',i.Index_SupplierName as '最后承运商' from TMS_OrderIndex i ,TMS_Devices t  where t.Device_IMEICode = i.Index_DeviceCode and LEN(i.Index_SupplierID )>=1
#               and i.Index_SrcClass =2
#               and LEN(i.Index_SupplierName )>=1
#               order by i.Index_CreateTime desc '''
#     df = pd.read_sql(sql=sql2, con=conn)
#     # print(df)
#     finnal_df = df.iloc[df.groupby(['设备编码']).apply(
#         lambda x: x['最后绑定时间'].idxmax())]
#     sql3 = '''select
#                 d.Device_IMEICode as '设备编码',
#                 d.Device_PhoneNo as '设备号码',
#                 d.Device_SIMid as 'SIM提供商',
#                 d.Device_IMSI as 'IMSI码',
#                 d.Device_OwnerType as '是否租用',
#                 d.Device_Type as '设备类型',
#                 d.Device_temperature as '是否温控',
#                 d.Device_Invalid as '是否禁用' ,
#                 c.Company_Name as '客户名称'
#                 from TMS_Devices d,TMS_Company c where
#                 d.Device_CompanyID = c.Company_ID
#                 and d.Device_Invalid =0
#            '''
#     sql3 = sql3
#     df2 = pd.read_sql(sql=sql3, con=conn)
#     df2.loc[df2['SIM提供商'] == 1, 'SIM提供商'] = '长沙移动'
#     df2.loc[df2['SIM提供商'] == 2, 'SIM提供商'] = '浙江移动'
#     df2.loc[df2['SIM提供商'] == 3, 'SIM提供商'] = '湖南物联网协会'
#     df2.loc[df2['是否租用'] == 1, '是否租用'] = '是'
#     df2.loc[df2['是否租用'] == 0, '是否租用'] = '否'
#     df2.loc[df2['设备类型'] == 1, '设备类型'] = '1代'
#     df2.loc[df2['设备类型'] == 2, '设备类型'] = '2代'
#     df2.loc[df2['设备类型'] == 3, '设备类型'] = '3代'
#     df2.loc[df2['是否温控'] == 1, '是否温控'] = '是'
#     df2.loc[df2['是否温控'] == 0, '是否温控'] = '否'
#     df2.loc[df2['是否禁用'] == 1, '是否禁用'] = '是'
#     df2.loc[df2['是否禁用'] == 0, '是否禁用'] = '否'
#     a = pd.merge(finnal_df, df2, on='设备编码', how='inner')
#     b = pd.merge(df2,a, on='设备编码', how='left', suffixes=('', '_y'))
#     b.drop(b.filter(regex='_y$').columns.tolist(), axis=1,inplace=True)
#     download_path = download_path + f'\{my_file_name}'
#
#     b.to_excel(download_path)  # 筛选后的数据生成excel
# excel_test()
