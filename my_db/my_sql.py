import sys
import os
sys.path.append("..")
sys.path.append(os.path.abspath("../../"))
import pymssql
import time
from collections import OrderedDict
from api_preceipt.api import page2
host =  "192.168.1.151"
username = "WLY"
password = "Wly2.@907"
database = 'WLY'

class my_sql():

    def __init__(self,host,username,password,database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.db = pymssql.connect(self.host, self.username, self.password, self.database, charset='utf8')
        Sales_data = {                     #第一次销售结构
            "Sales_Name": "",
            "Companys": ""
        }
        Companys_data = {                   #第二层公司名字 对应 第一层 Companys 节点
            "Id": "",
            "Count":"",
            "Company_Name": "",
            "Devices": ""
        }
        Devices_data = {                   #第三层 设备详细列表，对应第二层Devices节点
            "Id": "",
            "IMEI": ""
        }
        self.my_list =[]
    def find_comp(self,page=1,size=20):
        self.cursor = self.db.cursor()
        data = page2.paginate(page, size)
        global compList
        try:
            sql = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 and Company_Personal = '0'order by Company_ID offset {} row fetch next {} row only ".format(data['offset'],data['limit'])
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

    def find_Device(self,page=1,size=20,Device_CompanyID='189'):#offset a rows ,将前a条记录舍去，fetch next b rows only ，向后在读取b条数据。
                                        # 传入页数和每页显示数，返回公司名称和设备详情
        data = page2.paginate(page,size)
        global DeviceList
        self.cursor = self.db.cursor()
        try:
            sql = "select Device_IMEICode from TMS_Devices where Device_IMEICode like '351608086%' and Device_Invalid = '0' and Device_CompanyID ={} order by Device_IMEICode offset {} row fetch next {} row only ".format(Device_CompanyID,data['offset'],data['limit'])
            self.cursor.execute(sql)
            DeviceList =self.cursor.fetchall()
        except:
            return 'Error: unable to fecth data'
        finally:
            self.cursor.close()

            return DeviceList

    def Comp_Device(self,page=1,size=20,Device_CompanyID='189'):
        l= []

        DeviceList = self.find_Device(page,size)

        for i in DeviceList:
            l.append(i[0])
        return l

    def Device_Count(self,page=1,size=20):#传入页数和每页显示数，返回公司名称和设备数
        tt = time.time()
        data = page2.paginate(page, size)
        l=[]
        m=[]
        data2 = {
            "Company_Name":"",
            "Device_CompanyID":"",
            "Count":" ",
            "IMEI":""
        }
        data3={
            "id":"",
            "Company_Name": ""
        }
        try:
            self.cursor = self.db.cursor()
            compl = "select Company_ID,Company_Name from TMS_Company where Company_Invalid = 0 and Company_Personal = '0'order by Company_ID "
            self.cursor.execute(compl)
            compList =  self.cursor.fetchall()
            for i in compList:
                k = []
                sql = "SELECT COUNT(*) from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={}".format(i[0])
                self.cursor.execute(sql)
                Device_Count = self.cursor.fetchone()
                # Device_Count = Device_Count(size * page : page + size * page-1)
                if Device_Count[0] > 0:
                    id = 0
                    sql_2 = "select Device_IMEICode from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={} order by Device_IMEICode offset {} row fetch next {} row only ".format(i[0], data['offset'], data['limit'])
                    self.cursor.execute(sql_2)
                    DeviceList = self.cursor.fetchall()
                    # print(DeviceList)
                    for j in DeviceList:
                        id = id +1
                        data3["id"]=id
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

    def get_index_id(self,DeviceCode,page=1,size=20,desc = 1):
        self.cursor = self.db.cursor()
        data = page2.paginate(page, size)
        da = {
            'id': '',
            'CreateTime': ''
        }
        l = []
        if desc == 1:#按时间倒序排列
            try:
                sql = "select Index_ID  ,Index_CreateTime from  TMS_OrderIndex where  Index_RootOrderID = Index_ID and Index_DeviceCode = '{}' ORDER BY Index_CreateTime desc offset {} row fetch next {} row only ".format(DeviceCode,data['offset'], data['limit'])
                self.cursor.execute(sql)
                id= self.cursor.fetchall()
                for i in id:
                    da['id'] = i[0]
                    da['CreateTime'] = i[1].strftime('%Y-%m-%d %H:%M:%S')
                    l.append(da.copy())
            except:
                return 'Error: unable to fecth data'
            finally:
                self.cursor.close()
                return l
        else:#倒序顺序排列
            try:
                sql = "select Index_ID  ,Index_CreateTime from  TMS_OrderIndex where  Index_RootOrderID = Index_ID and Index_DeviceCode = '{}' ORDER BY Index_CreateTime  offset {} row fetch next {} row only ".format(DeviceCode,data['offset'], data['limit'])
                self.cursor.execute(sql)
                id= self.cursor.fetchall()
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

    def select_IMEI(self,Device_CompanyID):
        sql = "select Device_IMEICode from TMS_Devices where Device_IMEICode like '351608086%' and Device_CompanyID='{}' order by Device_IMEICode".format(Device_CompanyID)
        self.cursor = self.db.cursor()
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def find_count_and_List(self,Device_CompanyID=None):
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
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0  and d.Device_IMEICode like '351608086%'order by c.Company_ID"
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql)
            b = self.cursor.fetchall()
            k = []
            l = []
            s = []
            c={}
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
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_IMEICode like '351608086%' and d.Device_CompanyID not in {} order by c.Company_ID".format(Device_CompanyID)
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
                    m_m.append( Devices_data.copy())
                i['Companys'][0]["Devices"] = m_m
            # print('222222',l)

            return l

    def find_device_to_company_name(self,Company_Name):
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
        sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_IMEICode like '351608086%' and  c.Company_Name = '{}' order by d.Device_IMEICode".format(str(Company_Name))
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

    def find_device_to_company_name2(self,Company_Name):
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
        sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0  and d.Device_IMEICode like '351608086%' and  c.Company_Name like '%{}%' order by d.Device_IMEICode".format(str(Company_Name))
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

    def find_device_to_imei(self,imei):
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
        sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_IMEICode like '351608086%' and  d.Device_Invalid = 0  and  d.Device_IMEICode like'{}%' order by d.Device_IMEICode".format(
            str(imei))
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if len(res) > 0:
            cp_list =[]
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
        m_list =[]
        for i in res:

            Sales_data["Sales_Name"] = i["Sales_name"]

            sql_2 = "select Company_Name from TMS_Sales where Sales_name='{}'".format(i["Sales_name"])
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql_2)
            Company_Name = self.cursor.fetchall()
            ls = []
            for j in Company_Name:
                kk =self.find_device_to_company_name(j['Company_Name'])
                ls.append(kk)
                Sales_data["Companys"] =ls
                m_list.append(Sales_data.copy())
        m =self.find_device_not_in_sales()

        l =  m_list + m
        # print(l)
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
        m_list =[]
        s_n =[]
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
                kk =self.find_device_to_company_name(j['Company_Name'])
                ls.append(kk)

            # print(ls)
            Sales_data["Companys"] =ls
            m_list.append(Sales_data.copy())
        # print(m_list)
        m =self.find_device_not_in_sales()

        l =  m_list + m
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
            if i["Company_id"]!= None:
                k.append(i["Company_id"])
                k = sorted(list(set(k)))
        data = self.find_count_and_List(Device_CompanyID=k)
        # print('data',data)
        m.append(data.copy())
        return data

    def find_count_and_List2(self,Device_CompanyID=None):
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
        if Device_CompanyID ==None:
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0  and d.Device_IMEICode like '351608086%' order by c.Company_ID"
            self.cursor = self.db.cursor(as_dict=True)
            self.cursor.execute(sql)
            b = self.cursor.fetchall()
            # print(b)
            k = []
            l = []
            s = []
            c={}
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
            sql = "select  c.Company_Name, d.Device_IMEICode, d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_IMEICode like '351608086%'  and d.Device_CompanyID not in {} order by c.Company_ID".format(Device_CompanyID)
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
        sales_name ={
            'sales_name':'',
            'sales_company':''

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
            sales_name['sales_company'] =res2[0]['Sales_Company']
            m.append(sales_name.copy())
        return m

    def find_Company_name_by_sales_name(self,sales_name):
        if sales_name !="直销":
            Company_name ={
                'Company_name' :'',
                'Company_Id': '',
                'Count':''
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
                count_sql = "SELECT COUNT(*) as Count from TMS_Devices where Device_Invalid = '0' and Device_CompanyID ={}".format(res2[0]['Company_ID'])
                self.cursor.execute(count_sql)
                res3 = self.cursor.fetchall()
                Company_name['Count'] = res3[0]["Count"]
                Company_name['Company_Id'] = res2[0]['Company_ID']
                l.append(Company_name.copy())
            return l
        else:
            Company_name ={
                'Company_name' :'',
                'Company_Id': '',
                'Count':''
            }
            c = {}
            m = []
            cp_list = self.find_No_Sales_Companys()
            cp_id_sql ="select  c.Company_Name,  d.Device_CompanyID  from TMS_Devices  d inner join TMS_Company  c  on d.Device_CompanyID=c.Company_ID and d.Device_Invalid = 0 and d.Device_CompanyID not in{} order by c.Company_ID".format(cp_list)
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
        sql = " select Device_IMEICode from TMS_Devices where Device_IMEICode like '351608086%' and Device_Invalid = 0 and Device_CompanyID = '{}'".format(Company_Id)
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

    def fint_pactcode_by_imei(self,imei,page =1, size=20):
        p_data = {
            'Index_PactCode':'',
            'Index_FromTime':'',
            'Index_ToTime':'',
            'Company_Name':''
        }
        l = []
        data = page2.paginate(page, size)
        imei = str(imei)
        sql = " select  o.Index_PactCode, o.Index_FromTime, o.Index_ToTime,c.Company_Name from  TMS_OrderIndex o ,TMS_Company c where o.Index_DeviceCode = '{}' and o.index_ID = o.Index_RootOrderID and o.Index_CreatorCompanyID = c.Company_ID ORDER BY o.Index_FromTime DESC offset {} row fetch next {} row only ".format(imei,data['offset'],data['limit'])
        self.cursor = self.db.cursor(as_dict=True)
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        for i in res1:
            p_data['Index_PactCode'] = i['Index_PactCode']
            p_data['Index_FromTime'] = str(i['Index_FromTime'])
            p_data['Index_ToTime'] = str(i['Index_ToTime'])
            p_data['Company_Name'] = i['Company_Name']
            l.append(p_data.copy())
        return  l

    def find_Company_name_and_Device_list(self,sales_company):
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


def open_mysql():
    my = my_sql(host="192.168.1.151", username="WLY", password="Wly2.@907", database='WLY')
    return my


# a = open_mysql()
# # c = a.find_Device_list_by_Company_Id('189')
# c = a.find_Company_name_and_Device_list('北京')
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
#上海林内有限公司|RLN190528050|5030091
# b = a.find_count_and_List([63, 158, 167, 189, 197])
# print(b)
