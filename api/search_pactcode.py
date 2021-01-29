import json
import sys

import requests

sys.path.append("..")
import pandas as pd
from models import db, TMSOrderIndex, TMSSale, TMSDevice, User, Salesarea
from sqlalchemy import and_, or_


def get_child(id):
    k_l = []
    k_l.append(id)
    child = db.session.query(Salesarea).filter(Salesarea.parent_id == id, Salesarea.is_disable == 0).all()
    if len(child) != 0:
        for k in child:
            k_l.append(k.area_id)
    else:
        k_l.append(id)
    return k_l


global l_list
l_list = []


def find_all_child(id):
    global l_list
    l_list.append(id)
    child = db.session.query(Salesarea).filter(Salesarea.parent_id == id, Salesarea.is_disable == 0).all()
    if len(child) != 0:
        for i in child:
            l_list = l_list + get_child(i.area_id)
        return find_all_child(i.area_id)
    else:
        for k in child:
            l_list = l_list + get_child(k.area_id)
    l_list = list(set(l_list))
    return l_list


def get_all_id(id):
    u_id = db.session.query(User).filter(User.is_disable == 0, User.id == id).first()
    my_l = []
    if u_id.is_manager == 1:
        id = u_id.parent_id
        p_id = db.session.query(Salesarea).filter(Salesarea.is_disable == 0, Salesarea.area_id == id).first()
        l = find_all_child(p_id.parent_id)
        for area in l:
            rs = db.session.query(User).filter(User.is_disable == 0, User.parent_id == area).all()
            if rs:
                for k in rs:
                    my_l.append(k.id)
    else:
        my_l.append(id)
    global l_list
    l_list = []
    return my_l


def search_pactcode_by_imei(s_data, page, size, id=None):
    b_data = {
        'IMEI': '',
        'PactCode': '',
        'Company_Name': '',
    }
    s_data = {**b_data, **s_data}
    p_data = {
        'Index_PactCode': '',
        'Index_FromTime': '',
        'Index_ToTime': '',
        'Company_Name': '',
        'Company_ID': '',
        'Index_Code': '',
        'Order_Status': ''
    }
    l = []
    da = {
        "count": '',
        "datalist": ''
    }
    s_data['IMEI'] = "%" + s_data['IMEI'] + "%"
    s_data['PactCode'] = "%" + s_data['PactCode'] + "%"
    s_data['Company_Name'] = "%" + s_data['Company_Name'] + "%"
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        post_data = db.session.query(TMSOrderIndex.Index_PactCode,
                                     TMSOrderIndex.Index_FromTime,
                                     TMSOrderIndex.Index_ToTime,
                                     TMSSale.Company_Name,
                                     TMSDevice.Device_IMEICode,
                                     TMSSale.Company_Id,
                                     TMSOrderIndex.Index_Code,
                                     TMSOrderIndex.Index_Status,
                                     ).join(TMSDevice, TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex,
            TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode).filter(
            and_(TMSDevice.Device_Type.between(2, 3),
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 TMSOrderIndex.Index_Status.between(2, 16),
                 TMSSale.Is_disabled == 0,
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(
            TMSOrderIndex.Index_FromTime.desc()).with_for_update(read=True).paginate(
            int(page), int(size), False)
        res = post_data.items
        for i in res:
            p_data['Index_PactCode'] = i[0]
            p_data['Index_FromTime'] = str(i[1].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Index_ToTime'] = str(i[2].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Company_Name'] = i[3]
            p_data['Index_DeviceCode'] = i[4]
            p_data['Company_ID'] = i[5]
            p_data['Index_Code'] = i[6]
            p_data['Order_Status'] = i[7]
            l.append(p_data.copy())
        count = db.session.query(TMSOrderIndex, TMSSale, TMSDevice).join(TMSDevice,
                                                                         TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex, TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode).filter(
            and_(TMSDevice.Device_Type.between(2, 3),
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 TMSOrderIndex.Index_Status.between(2, 16),
                 TMSSale.Is_disabled == 0,
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).with_for_update(read=True).count()
        da["count"] = count
        da["datalist"] = l
        db.session.close()
    else:
        my_id = get_all_id(id)
        post_data = db.session.query(TMSOrderIndex.Index_PactCode,
                                     TMSOrderIndex.Index_FromTime,
                                     TMSOrderIndex.Index_ToTime,
                                     TMSSale.Company_Name,
                                     TMSDevice.Device_IMEICode,
                                     TMSSale.Company_Id,
                                     TMSOrderIndex.Index_Code,
                                     TMSOrderIndex.Index_Status,
                                     ).join(TMSDevice, TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex,
            TMSDevice.Device_CompanyID == TMSOrderIndex.Index_CreatorCompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 TMSOrderIndex.Index_CreatorCompanyID == TMSSale.Company_Id,
                 TMSOrderIndex.Index_Status.between(2, 32),
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSSale.user_id.in_(my_id),
                 TMSSale.Is_disabled == 0,
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(
            TMSOrderIndex.Index_FromTime.desc()).with_for_update(read=True).paginate(
            int(page), int(size), False)
        res = post_data.items
        for i in res:
            p_data['Index_PactCode'] = i[0]
            p_data['Index_FromTime'] = str(i[1].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Index_ToTime'] = str(i[2].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Company_Name'] = i[3]
            p_data['Index_DeviceCode'] = i[4]
            p_data['Company_ID'] = i[5]
            p_data['Index_Code'] = i[6]
            p_data['Order_Status'] = i[7]
            l.append(p_data.copy())
        count = db.session.query(TMSOrderIndex, TMSSale, TMSDevice).join(TMSDevice,
                                                                         TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex, TMSDevice.Device_CompanyID == TMSOrderIndex.Index_CreatorCompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 TMSOrderIndex.Index_Status.between(2, 32),
                 TMSOrderIndex.Index_CreatorCompanyID == TMSSale.Company_Id,
                 TMSSale.user_id.in_(my_id),
                 TMSSale.Is_disabled == 0,
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).with_for_update(read=True).count()
        da["count"] = count
        da["datalist"] = l
        db.session.close()
    return da


def search_pactcode_by_imei2(s_data, page, size, id=None):
    p_data = {
        'Index_PactCode': '',
        'Index_FromTime': '',
        'Index_ToTime': '',
        'Company_Name': '',
        'Company_ID': '',
        'Index_Code': '',
        'Order_Status': ''
    }
    l = []
    my_res = []
    da = {
        "count": '',
        "datalist": ''
    }
    a = db.session().query(User).filter(User.id == id).first()
    my_id = get_all_id(id)
    sales_sql = '''SELECT Company_Name,Company_Id from ERE.dbo.TMS_Sales where 1 = 1'''
    if 'Company_Name' in s_data.keys():
        cp_sql = '''and  Company_Name='{}' '''.format(s_data['Company_Name'])
        sales_sql =sales_sql + cp_sql
    sql = '''
        SELECT 
        t.Index_PactCode,
        t.Index_FromTime,
        t.Index_ToTime,
        t.Index_Code,
        t.Index_Status,
        d.Device_IMEICode,
        s.Company_Name,
        s.Company_Id
        from 
        WLY.dbo.TMS_Devices as d ,
        WLY.dbo.TMS_OrderIndex  as t,
        ({}) as s
        where 
        1=1 
        and 
        d.Device_IMEICode =t.Index_DeviceCode
        and
        s.Company_Id = d.Device_CompanyID
        and 
        d.Device_Type BETWEEN 2 and 3
        and t.Index_ID = t.Index_RootOrderID
        and t.Index_Status BETWEEN 2 and 16 '''.format(sales_sql)
    count_sql = '''
        SELECT 
        count(*) as count
        from 
        WLY.dbo.TMS_Devices as d ,
        WLY.dbo.TMS_OrderIndex  as t,
        ({}) as s
        where 
        1=1 
        and 
        d.Device_IMEICode =t.Index_DeviceCode
        and
        s.Company_Id = d.Device_CompanyID
        and 
        d.Device_Type BETWEEN 2 and 3
        and t.Index_ID = t.Index_RootOrderID
        and t.Index_Status BETWEEN 2 and 16'''.format(sales_sql)
    if 'PactCode' in s_data.keys():
        pact_sql = '''and t.Index_PactCode ='{}' '''.format(str(s_data['PactCode']))
        sql = sql + pact_sql
        count_sql = count_sql + pact_sql
    if 'IMEI' in s_data.keys():
        imei_sql = '''and d.Device_IMEICode='{}' '''.format(str(s_data['IMEI']))
        sql = sql + imei_sql
        count_sql = count_sql + imei_sql
    sql2 = ''' ORDER BY t.Index_FromTime desc offset {} rows fetch next {} rows only'''.format((page - 1) * size, size)
    if a.role_id:
        sql = sql + sql2
        res = db.session.execute(sql)
        result = res.fetchall()
        count_res = db.session.execute(count_sql)
        count = count_res.fetchall()
        for i in result:
            p_data['Index_PactCode'] = i[0]
            p_data['Index_FromTime'] = str(i[1].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Index_ToTime'] = str(i[2].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Company_Name'] = i[6]
            p_data['Index_DeviceCode'] = i[5]
            p_data['Company_ID'] = i[7]
            p_data['Index_Code'] = i[3]
            p_data['Order_Status'] = i[4]
            l.append(p_data.copy())
        da["count"] = count[0][0]
        da["datalist"] = l
        db.session.close()
    else:
        sales_sql = '''and user_id in {}'''.format(my_id)
        sql = '''
                SELECT 
                t.Index_PactCode,
                t.Index_FromTime,
                t.Index_ToTime,
                t.Index_Code,
                t.Index_Status,
                d.Device_IMEICode,
                s.Company_Name,
                s.Company_Id
                from 
                WLY.dbo.TMS_Devices as d ,
                WLY.dbo.TMS_OrderIndex  as t,
                ({}) as s
                where 
                1=1 
                and 
                d.Device_IMEICode =t.Index_DeviceCode
                and
                s.Company_Id = d.Device_CompanyID
                and 
                d.Device_Type BETWEEN 2 and 3
                and t.Index_ID = t.Index_RootOrderID
                and t.Index_Status BETWEEN 2 and 16 '''.format(sales_sql)
        sql = sql + sql2
        res = db.session.execute(sql)
        result = res.fetchall()
        count_res = db.session.execute(count_sql)
        count = count_res.fetchall()
        for i in result:
            p_data['Index_PactCode'] = i[0]
            p_data['Index_FromTime'] = str(i[1].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Index_ToTime'] = str(i[2].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Company_Name'] = i[6]
            p_data['Index_DeviceCode'] = i[5]
            p_data['Company_ID'] = i[7]
            p_data['Index_Code'] = i[3]
            p_data['Order_Status'] = i[4]
            l.append(p_data.copy())
        da["count"] = count[0][0]
        da["datalist"] = l
        db.session.close()
    return da

#
# data = {"page": 1, "size": 10000, "id": "84", "username": "超级管理员", "useraccount": "admin"}
# page = data['page']
# size = data['size']
# id = int(data['id'])
# a = search_pactcode_by_imei2(data, page, size, id)
# print(a)

# query = db.session.query(User)
# print(getattr(User, 'username'))
