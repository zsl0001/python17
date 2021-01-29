import json
from math import ceil

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import pymssql
import requests
from datetime import datetime
from myconfig import sqldb, mgdb, api_cfg, ere_cfg

base_url1 = "http://192.168.1.89:1001"


# base_url1 = "http://172.16.14.133:1001"


def get_lastSupName(id):
    url_1 = "/search/biz/log/device/{}/lastSupplier".format(id)
    url = base_url1 + url_1
    ret = requests.get(url)
    res = json.loads(ret.text)
    if res['data']['list']:
        lastSupName = res['data']['list'][0]['companyName']
    else:
        lastSupName = ''
    return lastSupName


def get_lastBindTime(id):
    url_1 = "/search/biz/log/device/{}/lastSupplier".format(id)
    url = base_url1 + url_1
    ret = requests.get(url)
    res = json.loads(ret.text)
    if res['data']['list']:
        lastBindTime = res['data']['list'][0]['timestamp']
        dateArray = datetime.fromtimestamp(float(eval(lastBindTime) / 1000))
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    else:
        otherStyleTime = ''
    return otherStyleTime


# timeStamp = 1381419600
# dateArray = datetime.fromtimestamp(timeStamp)
# otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
# print(otherStyleTime)
# get_lastBindTime(117904)


def get_all_device(data):
    conn = pymssql.connect(host=sqldb['host'], user=sqldb['username'], password=sqldb['password'], database='WLY')
    cursor = conn.cursor()
    page = data['page']
    size = data['size']
    sql = '''select  								
                            d.Device_IMEICode as imeicode,
                            d.Device_PhoneNo as phoneNo,
                            d.Device_SIMid as simid,
                            d.Device_InsertTime as insertTime,
                            d.Device_Invalid as invalid,
                            d.Device_Type as type,
                            d.Device_IMSI as imsi,
                            d.Device_OwnerType as ownerType,
                            d.Device_SIMBatch as Device_SIMBatch,
                            d.Device_temperature as temperature,
                            d.Device_Expiry_Starttime as expiry_starttime,
                            d.Device_Expiry_Endtime as expiry_endtime,
                            d.Device_ID as device_id,
                            c.Company_Name as companyName,
                            c.Company_Personal as company_personal,
                            c.Company_ID  as companyID from TMS_Devices d  left  join TMS_Company c on c.Company_ID = d.Device_CompanyID WHERE 1=1 {}  ORDER BY d.Device_InsertTime desc offset {} row fetch next {} row only'''
    sql1 = ''
    sql_count = '''
                SELECT 
                    count(*) as count
                from TMS_Devices d  left  join TMS_Company c on c.Company_ID = d.Device_CompanyID WHERE 1=1 {} '''
    my_l = []
    if 'invalid' in data.keys():
        my_l.append(data['invalid'])
        my_l = tuple(my_l)[0]
        s3 = "and Device_Invalid in (" + f"{my_l}" + ')'
        sql1 = sql1 + s3
    else:
        my_l = (0, 1)
        s3 = f"and Device_Invalid in {my_l}"
        sql1 = sql1 + s3
    if 'ownerType' in data.keys():
        ownerType = data['ownerType']
        if len(str(ownerType)) >= 1:
            sql1 = sql1 + f' and Device_OwnerType = {ownerType} '
    if 'imsi' in data.keys():
        imsi = data['imsi']
        if len(imsi) >= 1:
            sql1 = sql1 + f'and Device_IMSI = {imsi} '
    if 'type' in data.keys():
        type = data['type']
        if len(str(type)) >= 1:
            sql1 = sql1 + f'and Device_Type = {type} '
    if 'imeicode' in data.keys():
        imeicode = data['imeicode']
        if len(imeicode) >= 1:
            sql1 = sql1 + f"and Device_IMEICode like '%{imeicode}%'"
    if 'phoneNo' in data.keys():
        phoneNo = data['phoneNo']
        if len(phoneNo) >= 1:
            sql1 = sql1 + f"and Device_PhoneNo like '%{phoneNo}%' "
    if 'temperature' in data.keys():
        temperature = data['temperature']
        if len(str(temperature)) >= 1:
            sql1 = sql1 + f"and Device_temperature = {temperature} "
    if 'company_personal' in data.keys():
        company_personal = data['company_personal']
        s1 = f'and c.Company_Personal ={company_personal}'
        sql1 = sql1 + f"and Device_temperature = {temperature} "
    if 'companyName' in data.keys():
        companyName = data['companyName']
        if len(companyName) >= 1:
            s2 = f"and c.Company_Name like '%{companyName}%' and c.Company_Status = 2 and c.Company_Invalid = 0"
            sql1 = sql1 + s2
    sql = sql.format(sql1, (page - 1) * size, size)
    sql_count = sql_count.format(sql1)
    cursor.execute(sql_count)
    count = cursor.fetchall()[0][0]
    data = pd.read_sql_query(sql, con=conn)
    conn.close()
    data = data.fillna('')
    if len(data.index)!=0:
        data['insertTime'] = data['insertTime'].dt.strftime("%Y-%m-%d %H:%M:%S")
        data['expiry_starttime'] = data['expiry_starttime'].apply(
            lambda x: x if x == 'None' else str(x).split('.')[0])
        data['expiry_starttime'] = data['expiry_starttime'].apply(
            lambda x: x if x != '1900-01-01 00:00:00' else '')
        data['expiry_endtime'] = data['expiry_endtime'].apply(
            lambda x: x if x == 'None' else str(x).split('.')[0])
        data['expiry_endtime'] = data['expiry_endtime'].apply(
            lambda x: x if x != '1900-01-01 00:00:00' else '')
        data['get_lastSupName'] = data['device_id'].apply(get_lastSupName)
        data['get_lastBindTime'] = data['device_id'].apply(get_lastBindTime)
        datalist = data.to_dict(orient='records')
    else:
        datalist = []
    # device_id
    # data['']
    # datetime.datetime.fromtimestamp(timeStamp)
    rs_data = {
        'total_page': ceil(count / int(size)),
        'datalist': datalist,
        'total': count
    }
    return rs_data

# a = get_all_device(data={'size': 10, 'page': 1,'imeicode': "351608085313456"})
# print(a)
# conn = pymssql.connect(host='192.168.1.200', user='WLY', password='Wly2.techns@907', database='WLY')
# cursor = conn.cursor(as_dict=True)
# sql_count = '''
#                 SELECT
#                     count(*) as count
#                 from TMS_Devices d  left  join TMS_Company c on c.Company_ID = d.Device_CompanyID WHERE 1=1'''
# cursor.execute(sql_count)
# print(cursor.fetchall())
