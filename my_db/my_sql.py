import sys
sys.path.append("..")
import os
import datetime



import pymssql
import time
from collections import OrderedDict
from api import page2
from my_db import Models
from my_db import Models
from myconfig import mgdb, sqldb, api_cfg


class my_sql():

    def __init__(self, host, username, password, database):
        self.username = sqldb['username']
        self.password = sqldb['password']
        self.database = sqldb['database']
        self.host = sqldb['host']
        self.db = pymssql.connect(self.host, self.username, self.password, self.database, charset='utf8')
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": ""
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        self.my_list = []

    def find_comp(self, page=1, size=20):
        self.cursor = self.db.cursor()
        data = page2.paginate(page, size)
        global compList
        try:
            sql = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 and Company_Personal = '0'order by Company_ID offset {} row fetch next {} row only ".format(
                data['offset'], data['limit'])
            self.cursor.execute(sql)
            compList = self.cursor.fetchall()
        except:
            return 'Error: unable to fecth data'
        finally:
            self.cursor.close()

            return compList

    def find_all_comp(self):
        self.cursor = self.db.cursor()
        global compList
        try:
            sql = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 order by Company_ID "
            self.cursor.execute(sql)
            compList = self.cursor.fetchall()
        except:
            return 'Error: unable to fecth data'
        finally:
            self.cursor.close()
            return compList

    def find_Device(self, page=1, size=20,
                    Device_CompanyID='189'):  # offset a rows ,将前a条记录舍去，fetch next b rows only ，向后在读取b条数据。
        # 传入页数和每页显示数，返回公司名称和设备详情
        data = page2.paginate(page, size)
        global DeviceList
        self.cursor = self.db.cursor()
        try:
            sql = "select Device_IMEICode from TMS_Devices where Device_Type in ('2','3') and Device_Invalid = '0' and Device_CompanyID ={} order by Device_IMEICode offset {} row fetch next {} row only ".format(
                Device_CompanyID, data['offset'], data['limit'])
            self.cursor.execute(sql)
            DeviceList = self.cursor.fetchall()
        except:
            return 'Error: unable to fecth data'
        finally:
            self.cursor.close()

            return DeviceList

    def Comp_Device(self, page=1, size=20, Device_CompanyID='189'):
        l = []

        DeviceList = self.find_Device(page, size)

        for i in DeviceList:
            l.append(i[0])
        return l

    def Device_Count(self, page=1, size=20):  # 传入页数和每页显示数，返回公司名称和设备数
        tt = time.time()
        data = page2.paginate(page, size)
        l = []
        m = []
        data2 = {
            "Company_Name": "",
            "Device_CompanyID": "",
            "Count": " ",
            "IMEI": ""
        }
        data3 = {
            "id": "",
            "Company_Name": ""
        }
        try:
            self.cursor = self.db.cursor()
            compl = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 and Company_Personal = '0'order by Company_ID "
            self.cursor.execute(compl)
            compList = self.cursor.fetchall()
            for i in compList:
                k = []
                sql = "SELECT COUNT(*) from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={}".format(
                    i[0])
                self.cursor.execute(sql)
                Device_Count = self.cursor.fetchone()
                # Device_Count = Device_Count(size * page : page + size * page-1)
                if Device_Count[0] > 0:
                    id = 0
                    sql_2 = "select Device_IMEICode from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={} order by Device_IMEICode offset {} row fetch next {} row only ".format(
                        i[0], data['offset'], data['limit'])
                    self.cursor.execute(sql_2)
                    DeviceList = self.cursor.fetchall()
                    # print(DeviceList)
                    for j in DeviceList:
                        id = id + 1
                        data3["id"] = id
                        data3["Company_Name"] = j[0]
                        k.append(data3.copy())
                    data2["Device_CompanyID"] = i[0]
                    data2["Company_Name"] = i[1]
                    data2["Count"] = Device_Count[0]
                    data2["IMEI"] = k
                    l.append(data2.copy())
        except:
            return 'Error: unable to fecth data'
        finally:
            print('Time used: {} sec'.format(time.time() - tt))
            self.cursor.close()
            return l

    def get_index_id(self, DeviceCode, page=1, size=20, desc=1):
        self.cursor = self.db.cursor()
        data = page2.paginate(page, size)
        da = {
            'id': '',
            'CreateTime': ''
        }
        l = []
        if desc == 1:  # 按时间倒序排列
            try:
                sql = "select Index_ID  ,Index_CreateTime from  TMS_OrderIndex where  Index_RootOrderID = Index_ID and Index_DeviceCode = '{}' ORDER BY Index_CreateTime desc offset {} row fetch next {} row only ".format(
                    DeviceCode, data['offset'], data['limit'])
                self.cursor.execute(sql)
                id = self.cursor.fetchall()
                for i in id:
                    da['id'] = i[0]
                    da['CreateTime'] = i[1].strftime('%Y-%m-%d %H:%M:%S')
                    l.append(da.copy())
            except:
                return 'Error: unable to fecth data'
            finally:
                self.cursor.close()
                return l
        else:  # 倒序顺序排列
            try:
                sql = "select Index_ID  ,Index_CreateTime from  TMS_OrderIndex where  Index_RootOrderID = Index_ID and Index_DeviceCode = '{}' ORDER BY Index_CreateTime  offset {} row fetch next {} row only ".format(
                    DeviceCode, data['offset'], data['limit'])
                self.cursor.execute(sql)
                id = self.cursor.fetchall()
                for i in id:
                    da['id'] = i[0]
                    da['time'] = i[1].strftime('%Y-%m-%d %H:%M:%S')
                    l.append(da.copy())
            except:
                return 'Error: unable to fecth data'
            finally:
                self.cursor.close()
                return l

    def closeDb(self):
        ''' 数据库连接关闭 '''
        self.db.close()

    def test(self):
        sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 order by c.Company_ID"
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def select_IMEI(self, Device_CompanyID):
        sql = "select Device_IMEICode from TMS_Devices where Device_Type in ('2','3') and Device_CompanyID='{}' order by Device_IMEICode".format(
            Device_CompanyID)
        self.cursor = self.db.cursor()
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def find_count_and_List(self, Device_CompanyID=None):
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": ""
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        if Device_CompanyID == None:
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0  and d.Device_Type in('2','3') order by c.Company_ID"
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql)
            b = self.cursor.fetchall()
            k = []
            l = []
            s = []
            c = {}
            for item in b:
                c.setdefault(item['Company_Name'], {**item, 'count': 0})['count'] += 1
                k.append(item['Device_CompanyID'])
            m = list(c.values())
            k = sorted(list(set(k)))
            for i in k:
                for item in m:
                    if i == item['Device_CompanyID']:
                        Companys_data["Count"] = item['count']
                        Companys_data["Company_Name"] = item['Company_Name']
                        Companys_data["Id"] = item['Device_CompanyID']
                        l.append(Companys_data.copy())
            for i in l:
                m_m = []
                s_s = self.select_IMEI(i['Id'])
                Devices_data['Id'] = i['Id']
                for cc in range(0, i['Count']):
                    Companys_data["Id"] = cc
                    Companys_data["Company_Name"] = s_s[cc][0]
                    m_m.append(Companys_data.copy())
                i["Devices"] = m_m

            return l
        else:
            Device_CompanyID = tuple(Device_CompanyID)
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_Type in ('2','3') and d.Device_CompanyID not in {} order by c.Company_ID".format(
                Device_CompanyID)
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql)
            b = self.cursor.fetchall()
            k = []
            l = []
            c = {}
            for item in b:
                c.setdefault(item['Company_Name'], {**item, 'count': 0})['count'] += 1
                k.append(item['Device_CompanyID'])
            m = list(c.values())
            k = sorted(list(set(k)))
            for i in k:
                for item in m:
                    if i == item['Device_CompanyID']:
                        ll = []
                        Companys_data["Count"] = item['count']
                        Companys_data["Company_Name"] = item['Company_Name']
                        Companys_data["Id"] = item['Device_CompanyID']
                        ll.append(Companys_data.copy())
                        Sales_data["Sales_Name"] = "无归属"
                        Sales_data["Companys"] = ll
                        l.append(Sales_data.copy())
            for i in l:
                m_m = []
                s_s = self.select_IMEI(i['Companys'][0]['Id'])
                for cc in range(0, i['Companys'][0]['Count']):
                    Devices_data["Id"] = cc
                    Devices_data["IMEI"] = s_s[cc][0]
                    m_m.append(Devices_data.copy())
                i['Companys'][0]["Devices"] = m_m
            # print('222222',l)

            return l

    def find_device_to_company_name(self, Company_Name):
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": ""
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_Type in ('2','3') and  c.Company_Name = '{}' order by d.Device_IMEICode".format(
            str(Company_Name))
        self.cursor = self.db.cursor()
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if len(res) > 0:
            l = []
            Companys_data["Count"] = len(res)
            Companys_data["Company_Name"] = res[0][0]
            Companys_data["Id"] = res[0][2]
            count = 0
            for i in res:
                count = count + 1
                Devices_data["Id"] = count
                Devices_data["IMEI"] = i[1]
                # print(self.Devices_data)
                l.append(Devices_data.copy())

            Companys_data["Devices"] = l
            return Companys_data
        else:
            return "暂无数据"

    def find_device_to_company_name2(self, Company_Name):
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": ""
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0  and d.Device_Type in ('2','3') and  c.Company_Name like '%{}%' order by d.Device_IMEICode".format(
            str(Company_Name))
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if len(res) > 0:
            cp_list = []
            m = []
            for i in res:
                id = 0
                cp_list.append(i['Company_Name'])
                cp_list = sorted(list(set(cp_list)))

            for j in cp_list:
                count = 0
                l = []
                for k in res:
                    if j == k['Company_Name']:
                        Companys_data["Company_Name"] = j
                        count = count + 1
                        Companys_data["Id"] = k['Device_CompanyID']
                        Devices_data["Id"] = count
                        Devices_data["IMEI"] = k['Device_IMEICode']
                        l.append(Devices_data.copy())
                Companys_data["Devices"] = l
                Companys_data['Count'] = len(l)
                m.append(Companys_data.copy())
            return m
        else:
            return '暂无数据'

    def find_device_to_imei(self, imei):
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": ""
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Type in ('2','3') and  d.Device_Invalid = 0  and  d.Device_IMEICode like'{}%' order by d.Device_IMEICode".format(
            str(imei))
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if len(res) > 0:
            cp_list = []
            m = []
            for i in res:
                id = 0
                cp_list.append(i['Company_Name'])
                cp_list = sorted(list(set(cp_list)))
            for j in cp_list:
                count = 0
                l = []
                for k in res:
                    if j == k['Company_Name']:
                        Companys_data["Company_Name"] = j
                        count = count + 1
                        Companys_data["Id"] = k['Device_CompanyID']
                        Devices_data["Id"] = count
                        Devices_data["IMEI"] = k['Device_IMEICode']
                        l.append(Devices_data.copy())
                Companys_data["Devices"] = l
                Companys_data["Count"] = len(l)
                m.append(Companys_data.copy())
            return m
        else:
            return '暂无数据'

    def Sales_device(self):
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": []
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        sql = "select Sales_name,Company_Id from TMS_Sales group by Sales_name,Company_Id"
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        m_list = []
        for i in res:

            Sales_data["Sales_Name"] = i["Sales_name"]

            sql_2 = "select Company_Name from TMS_Sales where Sales_name='{}'".format(i["Sales_name"])
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql_2)
            Company_Name = self.cursor.fetchall()
            ls = []
            for j in Company_Name:
                kk = self.find_device_to_company_name(j['Company_Name'])
                ls.append(kk)
                Sales_data["Companys"] = ls
                m_list.append(Sales_data.copy())
        m = self.find_device_not_in_sales()
        l = m_list + m
        return l

    def Sales_device2(self):
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": []
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        sql = "select Sales_name,Company_Id from TMS_Sales group by Sales_name,Company_Id"
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        m_list = []
        s_n = []
        for i in res:
            s_n.append(i["Sales_name"])
            s_n = sorted(list(set(s_n)))

        for s_n in s_n:
            ls = []
            sql_2 = "select Company_Name from TMS_Sales where Sales_name='{}'".format(s_n)
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql_2)
            Sales_data["Sales_Name"] = s_n
            Company_Name = self.cursor.fetchall()
            for j in Company_Name:
                kk = self.find_device_to_company_name(j['Company_Name'])
                ls.append(kk)

            # print(ls)
            Sales_data["Companys"] = ls
            m_list.append(Sales_data.copy())
        # print(m_list)
        m = self.find_device_not_in_sales()

        l = m_list + m
        # print(l)
        return l

    def find_device_not_in_sales(self):
        # dat = {
        #     "Sales_Name":'',
        #     "Companys":''
        # }
        sql = "select Company_id from TMS_Sales order by Company_id"
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        # print(res1)
        k = []
        m = []
        for i in res1:
            if i['Company_id'] is not None:
                k.append(i["Company_id"])
                k = sorted(list(set(k)))
        data = self.find_count_and_List(Device_CompanyID=k)
        # print('data',data)
        m.append(data.copy())
        return data

    def find_count_and_List2(self, Device_CompanyID=None):
        Sales_data = {  # 第一次销售结构
            "Sales_Name": "",
            "Companys": ""
        }
        Companys_data = {  # 第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count": "",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {  # 第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        if Device_CompanyID == None:
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0  and d.Device_Type in ('2','3') order by c.Company_ID"
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql)
            b = self.cursor.fetchall()
            # print(b)
            k = []
            l = []
            s = []
            c = {}
            for item in b:
                c.setdefault(item['Company_Name'], {**item, 'count': 0})['count'] += 1
                k.append(item['Device_CompanyID'])
            m = list(c.values())
            k = sorted(list(set(k)))
            for i in k:
                for item in m:
                    if i == item['Device_CompanyID']:
                        # print(item)
                        Companys_data["Count"] = item['count']
                        Companys_data["Company_Name"] = item['Company_Name']
                        Companys_data["Id"] = item['Device_CompanyID']
                        l.append(Companys_data.copy())
            # print(l)
            for i in l:
                m_m = []
                s_s = self.select_IMEI(i['Id'])
                # self.Devices_data['Device_CompanyID'] = i['Id']
                for cc in range(0, i['Count']):
                    Companys_data["Id"] = cc
                    Companys_data["Company_Name"] = s_s[cc][0]
                    m_m.append(Companys_data.copy())
                i["Devices"] = m_m

            return l
        else:
            Device_CompanyID = tuple(Device_CompanyID)
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_Type in ('2','3')  and d.Device_CompanyID not in {} order by c.Company_ID".format(
                Device_CompanyID)
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql)
            b = self.cursor.fetchall()
            k = []
            l = []
            c = {}
            for item in b:
                c.setdefault(item['Company_Name'], {**item, 'count': 0})['count'] += 1
                k.append(item['Device_CompanyID'])
            m = list(c.values())
            k = sorted(list(set(k)))
            for i in k:
                for item in m:
                    if i == item['Device_CompanyID']:
                        Companys_data["Count"] = item['count']
                        Companys_data["Company_Name"] = item['Company_Name']
                        Companys_data["Id"] = item['Device_CompanyID']
                        l.append(Companys_data.copy())
            # print(l)
            for i in l:
                m_m = []
                s_s = self.select_IMEI(i['Id'])
                # self.Devices_data['Device_CompanyID'] = i['Device_CompanyID']
                for cc in range(0, i['Count']):
                    Devices_data["Id"] = cc
                    Devices_data["IMEI"] = s_s[cc][0]
                    m_m.append(Devices_data.copy())
                i["Devices"] = m_m
            # print(l)
            return l

    def get_sales_name(self):
        sales_name = {
            'sales_name': '',
            'sales_company': ''

        }
        sql = " select Sales_name from TMS_Sales  order by Sales_name "
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        k = []
        m = []
        for i in res1:
            k.append(i["Sales_name"])
            k = sorted(list(set(k)))
        for j in k:
            sales_name['sales_name'] = j
            sql2 = " select Sales_Company from TMS_Sales where Sales_name = '{}'".format(j)
            self.cursor.execute(sql2)
            res2 = self.cursor.fetchall()
            sales_name['sales_company'] = res2[0]['Sales_Company']
            m.append(sales_name.copy())
        return m

    def find_Company_name_by_sales_name(self, sales_name):
        if sales_name != "直销":
            Company_name = {
                'Company_name': '',
                'Company_Id': '',
                'Count': ''
            }
            name_sql = " select Company_name from TMS_Sales  where Sales_name ='{} '".format(sales_name)
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(name_sql)
            res1 = self.cursor.fetchall()
            l = []
            for i in res1:
                Company_name['Company_name'] = i['Company_name']
                id_sql = " select Company_ID from TMS_Sales  where Company_name ='{} '".format(i['Company_name'])
                self.cursor.execute(id_sql)
                res2 = self.cursor.fetchall()
                count_sql = "SELECT COUNT(*) as Count from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={}".format(
                    res2[0]['Company_ID'])
                self.cursor.execute(count_sql)
                res3 = self.cursor.fetchall()
                Company_name['Count'] = res3[0]["Count"]
                Company_name['Company_Id'] = res2[0]['Company_ID']
                l.append(Company_name.copy())
            return l
        else:
            Company_name = {
                'Company_name': '',
                'Company_Id': '',
                'Count': ''
            }
            c = {}
            m = []
            cp_list = self.find_No_Sales_Companys()
            cp_id_sql = "select  c.Company_Name,  d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_CompanyID not in{} order by c.Company_ID".format(
                cp_list)
            self.cursor.execute(cp_id_sql)
            res3 = self.cursor.fetchall()
            for item in res3:
                c.setdefault(item['Company_Name'], {**item, 'count': 0})['count'] += 1
            c = list(c.values())
            # print(c)
            for i in c:
                Company_name['Company_name'] = i['Company_Name']
                Company_name['Company_Id'] = i['Device_CompanyID']
                Company_name['count'] = i['count']
                m.append(Company_name.copy())
            # print(Company_name)
            return m

    def find_Device_list_by_Company_Id(self, Company_Id):
        Device_list = {
            'IMEI': ''
        }
        sql = " select Device_IMEICode from TMS_Devices where Device_Type in ('2','3') and Device_Invalid = 0 and Device_CompanyID = '{}'".format(
            Company_Id)
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        l = []
        for i in res1:
            Device_list['IMEI'] = i['Device_IMEICode']
            l.append(Device_list.copy())
        return l

    def find_No_Sales_Companys(self):
        sql = " select Company_Id from TMS_Sales  where Sales_name !='直销'"
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        l = []
        for i in res1:
            l.append(i['Company_Id'])
        return tuple(l)

    def fint_pactcode_by_imei(self, page=1, size=20):
        p_data = {
            'Index_PactCode': '',
            'Index_FromTime': '',
            'Index_ToTime': '',
            'Company_Name': ''
        }
        l = []
        da = {
            "count": '',
            "datalist": ''
        }
        data = page2.paginate(page, size)
        # imei = str(imei)
        # sql = " select  o.Index_PactCode, o.Index_FromTime, o.Index_ToTime,c.Company_Name from  TMS_OrderIndex o ,TMS_Company c where o.Index_DeviceCode = '{}' and o.index_ID = o.Index_RootOrderID and o.Index_CreatorCompanyID = c.Company_ID ORDER BY o.Index_FromTime DESC offset {} row fetch next {} row only ".format(
        #     imei, data['offset'], data['limit'])

        sql = " select  o.Index_DeviceCode,o.Index_PactCode, o.Index_FromTime, o.Index_ToTime,c.Company_Name from  TMS_OrderIndex o ,TMS_Company c , TMS_Devices t where t.Device_IMEICode=o.Index_DeviceCode and t.Device_Type in ('2','3') and o.index_ID = o.Index_RootOrderID and o.Index_CreatorCompanyID = c.Company_ID ORDER BY o.Index_FromTime DESC offset {} row fetch next {} row only ".format(
            data['offset'], data['limit'])
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        for i in res1:
            p_data['Index_PactCode'] = i['Index_PactCode']
            p_data['Index_FromTime'] = str(i['Index_FromTime'])
            p_data['Index_ToTime'] = str(i['Index_ToTime'])
            p_data['Company_Name'] = i['Company_Name']
            p_data['Index_DeviceCode'] = i['Index_DeviceCode']
            l.append(p_data.copy())
        con = "select  count(*) as count from  TMS_OrderIndex o ,TMS_Company c , TMS_Devices t where t.Device_IMEICode=o.Index_DeviceCode and t.Device_Type in ('2','3') and o.index_ID = o.Index_RootOrderID and o.Index_CreatorCompanyID = c.Company_ID "
        self.cursor.execute(con)
        res2 = self.cursor.fetchall()
        count = res2[0]['count']
        da['count'] = count
        da['datalist'] = l
        return da

    def find_Company_name_and_Device_list(self, sales_company):
        m = []
        data1 = self.get_sales_name()
        for i in data1:
            data = {
                'sales_Name': '',
                'content': ''
            }
            data2 = {
                'Company_name': '',
                'Company_Id': '',
                'Count': '',
                'IMEI': ''
            }
            data['sales_Name'] = i['sales_name']
            if i['sales_company'] == sales_company:
                da2 = self.find_Company_name_by_sales_name(i['sales_name'])
                for k in da2:
                    data2['Company_name'] = k['Company_name']
                    data2['Company_Id'] = k['Company_Id']
                    data2['Count'] = k['Count']
                    da3 = self.find_Device_list_by_Company_Id(k['Company_Id'])
                    data2['IMEI'] = da3
                    data['content'] = data2
                    m.append(data.copy())
        return m

    def find_Sales_and_Device_list(self, page=1, size=20):
        dat = {
            'Device_IMEICode': '',
            'Device_Expiry_Starttime': '',
            'Device_Expiry_Endtime': '',
            'Sales_name': '',
            'Company_Name': '',
            'Company_ID': '',
            'Device_Status': '',
            'lithium': ''
        }
        res = {
            'total': '',
            'datalist': '',
            'Seven': '',  # 7天过期
            'Sixty': '',  # 60天过期
            'expire': ''  # 已过期
        }
        expire_c = 0
        expire7_c = 0
        expire60_c = 0

        l = []
        data = page2.paginate(page, size)
        sql = "select  D.Device_IMEICode, D.Device_Expiry_Starttime,D.Device_Expiry_Endtime,S.Sales_name,S.Company_Name,S.Company_Id  from TMS_Devices D  inner join TMS_Sales S on D.Device_Invalid = 0 and S.Company_Id = D.Device_CompanyID and  D.Device_Type in('3','2') ORDER BY S.Company_Id  offset {} row fetch next {} row only".format(
            data['offset'], data['limit'])
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()

        self.cursor = self.db.cursor()
        count_sql = "select  count(*) from TMS_Devices D  inner join TMS_Sales S on D.Device_Invalid = 0 and S.Company_Id = D.Device_CompanyID and  D.Device_Type in('3','2')"
        self.cursor.execute(count_sql)
        count = self.cursor.fetchall()
        b = datetime.datetime.now()
        for i in res1:
            if i['Device_IMEICode'][8] == '6':
                st = Models.Status.objects(devId=str(i['Device_IMEICode'])).order_by('-devId').limit(1)
                dat['Device_IMEICode'] = i['Device_IMEICode']
                dat['Sales_name'] = i['Sales_name']
                dat['Company_Name'] = i['Company_Name']
                dat['Company_ID'] = i['Company_Id']
                #
                if str(i['Device_Expiry_Endtime']) in ['None', '1900-01-01 00:00:00'] and str(
                        i['Device_Expiry_Starttime']) in ['None', '1900-01-01 00:00:00']:
                    dat['Device_Expiry_Endtime'] = ' '
                    dat['Device_Expiry_Starttime'] = ' '
                else:
                    # print(str(i['Device_Expiry_Endtime']),str(i['Device_Expiry_Starttime']))
                    dat['Device_Expiry_Endtime'] = i['Device_Expiry_Endtime'].strftime("%Y-%m-%d %H:%M:%S")
                    dat['Device_Expiry_Starttime'] = i['Device_Expiry_Starttime'].strftime("%Y-%m-%d %H:%M:%S")

                if len(st) != 0:
                    for j in st:
                        dat['lithium'] = j.lithium
                        if (b - self.get_location_time(j.date)).total_seconds() > 420:
                            d = Models.SleepNotice.objects(imei=str(j.devId)).limit(1)
                            for m in d:
                                if m.date > j.date:
                                    dat['Device_Status'] = '休眠'
                                else:
                                    dat['Device_Status'] = '离线'
                        else:
                            dat['Device_Status'] = '在线'
                else:
                    dat['Device_Status'] = '离线'
                    dat['lithium'] = '0'
                l.append(dat.copy())
                dat.clear()
            elif i['Device_IMEICode'][8] == '7':
                st = Models.Log.objects(imei=str(i['Device_IMEICode'])).order_by('-imei').limit(1)

                dat['Device_IMEICode'] = i['Device_IMEICode']
                dat['Sales_name'] = i['Sales_name']
                dat['Company_Name'] = i['Company_Name']
                dat['Company_ID'] = i['Company_Id']
                #
                if str(i['Device_Expiry_Endtime']) in ['None', '1900-01-01 00:00:00'] and str(
                        i['Device_Expiry_Starttime']) in ['None', '1900-01-01 00:00:00']:
                    dat['Device_Expiry_Endtime'] = ' '
                    dat['Device_Expiry_Starttime'] = ' '
                else:
                    # print(str(i['Device_Expiry_Endtime']),str(i['Device_Expiry_Starttime']))
                    dat['Device_Expiry_Endtime'] = i['Device_Expiry_Endtime'].strftime("%Y-%m-%d %H:%M:%S")
                    dat['Device_Expiry_Starttime'] = i['Device_Expiry_Starttime'].strftime("%Y-%m-%d %H:%M:%S")
                if len(st) != 0:
                    for j in st:
                        dat['lithium'] = str(j.content).split(',')[-1]
                        if (b - self.get_location_time(j.time)).total_seconds() > 420:
                            d = Models.SleepNotice.objects(imei=str(j.imei)).limit(1)
                            for m in d:
                                if m.date > j.date:
                                    dat['Device_Status'] = '休眠'
                                else:
                                    dat['Device_Status'] = '离线'
                        else:
                            dat['Device_Status'] = '在线'
                else:
                    dat['Device_Status'] = '离线'
                    dat['lithium'] = '0'
                l.append(dat.copy())
                dat.clear()

        res['datalist'] = l
        res['total'] = count[0][0]
        sql_3 = "SELECT D.Device_Expiry_Starttime,D.Device_Expiry_Endtime,D.Device_IMEICode from TMS_Devices D ,TMS_Sales S where D.Device_Type in ('3','2') and D.Device_Invalid = 0 AND S.Company_Id = D.Device_CompanyID"
        self.cursor.execute(sql_3)
        res3 = self.cursor.fetchall()
        for i in res3:
            if i[1] is not None and i[0] != i[1]:
                # c = self.Caltime(str(i[1]).split(' ')[0], str(b.strftime("%Y-%m-%d")))
                c = self.Caltime(str(b.strftime("%Y-%m-%d")), str(i[1]).split(' ')[0])  # 当前时间-到期时间
                if c != '0:00:00':
                    c = eval(c)
                    if 0 < c <= 7:
                        expire7_c = expire7_c + 1
                    elif 7 < c <= 60:
                        expire60_c = expire60_c + 1
                    elif c > 60:

                        expire_c = expire_c + 1
            res['Seven'] = expire7_c
            res['Sixty'] = expire60_c
            res['expire'] = expire_c
        return res

    def find_user_pwd(self, username):
        sql = "SELECT User_Password FROM TMS_User where User_Account ='{}'".format(username)

        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        return res1

    @staticmethod
    def get_location_time(t):
        t = t + +datetime.timedelta(hours=8)
        return t

    def find_device_list_by_sales_company(self, sales_company):
        data = {
            "Sales_name": "",
            "Total": "",
            "Companys": ""
        }
        company = {
            "Company_Name": "",
            "Total": "",
            "Company_Id": "",
            "IMEI": ""
        }
        l = []
        count = 0
        sql = "SELECT Sales_name from TMS_Sales where Sales_Company = '{}' Group by Sales_name".format(sales_company)
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        for i in res1:
            m = []
            data["Sales_name"] = i["Sales_name"]
            sql_Cp = "SELECT Company_Name,Company_Id from TMS_Sales where Sales_name = '{}' ".format(i["Sales_name"])
            self.cursor.execute(sql_Cp)
            res2 = self.cursor.fetchall()
            for k in res2:
                p = []
                count: int = 0
                company["Company_Name"] = k["Company_Name"]
                company["Company_Id"] = k["Company_Id"]
                sql2 = "select Device_IMEICode from TMS_Devices where Device_CompanyID = '{}' and Device_Invalid = 0 and Device_Type in ('2','3')".format(
                    k["Company_Id"])
                self.cursor.execute(sql2)
                res2 = self.cursor.fetchall()
                for d in res2:
                    m_m = dict(Devices="")
                    m_m["Devices"] = d["Device_IMEICode"]
                    p.append(m_m.copy())
                company["IMEI"] = p
                company["Total"] = len(p)
                m.append(company.copy())
                data["Companys"] = m
                for dd in m:
                    count = dd['Total'] + count
                data["Total"] = count
            l.append(data.copy())
        return l

    # 计算两个日期相差天数，自定义函数名，和两个日期的变量名。
    def Caltime(self, date1, date2):
        # %Y-%m-%d为日期格式，其中的-可以用其他代替或者不写，但是要统一，同理后面的时分秒也一样；可以只计算日期，不计算时间。
        # date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
        # date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
        date1 = time.strptime(date1, "%Y-%m-%d")
        date2 = time.strptime(date2, "%Y-%m-%d")
        # 根据上面需要计算日期还是日期时间，来确定需要几个数组段。下标0表示年，小标1表示月，依次类推...
        # date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
        # date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
        date1 = datetime.datetime(date1[0], date1[1], date1[2])
        date2 = datetime.datetime(date2[0], date2[1], date2[2])
        # 返回两个变量相差的值，就是相差天数

        return str(date1 - date2).split(' ')[0]


def open_mysql():
    my = my_sql(**sqldb)
    return my


a = open_mysql()
# c = a.fint_pactcode_by_imei(1,20)
# c = a.find_Sales_and_Device_list(1, 20000)
# print(c)
# # c = a.find_Sales_and_Device_list(1,20)
# print(c)
# print(len(c))
# b=a.find_count_and_List2()
# # #

# c = a.find_device_to_company_name("脱普日用化学品有限公司")
# print(c)


# d = a.find_device_to_company_name2("北京")
# # d = a.find_device_to_imei("351608086")
# d = a.Sales_device2()
# e = a.find_device_not_in_sales()
# print(e)
# 上海林内有限公司|RLN190528050|5030091
# b = a.find_count_and_List([63, 158, 167, 189, 197])
# print(b)

# b= a.find_Sales_and_Device_list(1,10)
# print(b)
