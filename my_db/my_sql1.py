import sys
import os
sys.path.append("..")
sys.path.append(os.path.abspath("../../"))
import pymssql
import pandas as pd
import copy
from api_preceipt.api import page2

host =  "192.168.1.151"
user = "WLY"
password = "Wly2.@907"
db = 'WLY'

class my_sql():
    def __init__(self,host=host,user=user,password=password,db=db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db

    def __getconnect(self):
        if not self.db:
            raise(ValueError,'没有设置数据信息')
        conn = pymssql.connect(host = self.host,
                                    user = self.user,
                                    password = self.password,
                                    database = self.db,
                                    charset = "utf8")
        return conn
        # cur = self.conn.cursor()
        # if not cur:
        #     raise (ValueError,'数据连接失败')
        # else:
        #     return cur

    def find_comp(self,page=1,size=10):
        cur = self.__getconnect()
        data = page2.paginate(page, size)
        sql = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 and Company_Personal = '0'order by Company_ID offset {} row fetch next {} row only ".format(data['offset'],data['limit'])
        cur.execute(sql)
        compList = cur.fetchall()
        self.conn.close()
        return compList

    def find_all_comp(self):
        cur = self.__getconnect()
        sql = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 order by Company_ID "
        cur.execute(sql)
        compList = cur.fetchall()
        self.conn.close()
        return compList

    def find_Device(self,page=1,size=10,Device_CompanyID='189'):#offset a rows ,将前a条记录舍去，fetch next b rows only ，向后在读取b条数据。
                                        # 传入页数和每页显示数，返回公司名称和设备详情
        data = page2.paginate(page,size)
        # print(data['offset'],data['limit'])
        cur = self.__getconnect()
        sql = "select Device_IMEICode from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={} order by Device_IMEICode offset {} row fetch next {} row only ".format(Device_CompanyID,data['offset'],data['limit'])
        cur.execute(sql)
        DeviceList = cur.fetchall()
        self.conn.close()
        return DeviceList


    def Comp_Device(self,page=1,size=10,Device_CompanyID='189'):
        l= []
        DeviceList = self.find_Device(page,size)
        for i in DeviceList:
            l.append(i[0])
        return l


    def Device_Count(self,page=1,size=20):#传入页数和每页显示数，返回公司名称和设备数
        data = page2.paginate(page, size)
        cur = self.__getconnect()
        l=[]
        k=[]
        data2 = {
            "Company_Name":"",
            "Device_CompanyID":"",
            "Count":" ",
            "IMEI":""
        }
        compl = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 and Company_Personal = '0'order by Company_ID "
        cur.execute(compl)
        compList =  cur.fetchall()
        for i in compList:
            sql = "SELECT COUNT(*) from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={}".format(i[0])
            cur.execute(sql)
            Device_Count = cur.fetchone()
            # Device_Count = Device_Count(size * page : page + size * page-1)
            if Device_Count[0] > 0:
                sql_2 = "select Device_IMEICode from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={} order by Device_IMEICode offset {} row fetch next {} row only ".format(i[0], data['offset'], data['limit'])
                cur.execute(sql_2)
                DeviceList = cur.fetchall()
                for j in DeviceList:
                    k.append(j[0])
                data2["Device_CompanyID"] = i[0]
                data2["Company_Name"] = i[1]
                data2["Count"] = Device_Count[0]
                data2["IMEI"] = DeviceList
                l.append(data2.copy())
        self.conn.close()
        return l

    def get_index_id(self,DeviceCode,page=1,size=10,desc = 1):
        data = page2.paginate(page, size)
        da = {
            'id': '',
            'CreateTime': ''
        }
        l = []
        if desc == 1:#按时间倒序排列
            sql = "select Index_ID  ,Index_CreateTime from  TMS_OrderIndex where  Index_RootOrderID = Index_ID and Index_DeviceCode = '{}' ORDER BY Index_CreateTime desc offset {} row fetch next {} row only ".format(DeviceCode,data['offset'], data['limit'])
            cur = self.__getconnect()
            cur.execute(sql)
            id= cur.fetchall()
            for i in id:
                da['id'] = i[0]
                da['CreateTime'] = i[1].strftime('%Y-%m-%d %H:%M:%S')
                l.append(da.copy())
        else:#倒序顺序排列
            sql = "select Index_ID  ,Index_CreateTime from  TMS_OrderIndex where  Index_RootOrderID = Index_ID and Index_DeviceCode = '{}' ORDER BY Index_CreateTime  offset {} row fetch next {} row only ".format(DeviceCode,data['offset'], data['limit'])
            cur = self.__getconnect()
            cur.execute(sql)
            id= cur.fetchall()
            for i in id:
                da['id'] = i[0]
                da['time'] = i[1].strftime('%Y-%m-%d %H:%M:%S')
                l.append(da.copy())
        self.conn.close()
        return  l

    # def Device_Count(self,page=1,size=20):#传入页数和每页显示数，返回公司名称和设备数
    #     c = 0
    #     data = page2.paginate(page, size)
    #     conn = self.__getconnect()
    #     compl = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 and Company_Personal = '0'order by Company_ID "
    #     r = pd.read_sql(compl, conn)
    #     l = r.to_json()
    #     m = []
    #     # print(r)
    #     #print(l)
    #     for i in r['Company_ID']:
    #         sql = "SELECT COUNT(*) as count from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={}".format(i)
    #         r2 = pd.read_sql(sql, conn)
    #         d = r[r.Company_ID == i].index.to_list()
    #         r.loc[d[0], 'count'] = r2.loc[0, 'count']
    #     r = r[r['count']>0]
    #     # print(r.to_json())
    #     for k in r['Company_ID']:
    #         sql_2 = "select Device_CompanyID,Device_IMEICode from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={} order by Device_IMEICode ".format(k)
    #         r3 = pd.read_sql(sql_2,conn)
    #         print(r3)
    #     return r


#
a = my_sql()
# print(a.find_comp())
# print(a.find_Device())

a.Device_Count()
# a.Comp_Device(1,10)
#   select * from TMS_OrderIndex  order by Index_ID offset 2 row fetch next 100 row only
# c = a.get_index_id('351608085019920')
# print(c)
