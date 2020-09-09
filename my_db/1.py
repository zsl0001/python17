from datetime import datetime
from time import sleep

import requests
import json
import base64
import time

post_data = {
    "username": 'chenjixian',
    "password": "123456",
    'uid':'65c3ea14958c11eabe8a1831bf501dcb'
}
# a = requests.post(url="https://fv1.wlyuan.com/login", data=json.dumps(post_data))
a = requests.post(url="http://192.168.1.52:7777/api/login", data=json.dumps(post_data))
# post_data1 = {
#     "username": 'liuyang',
#     "password": "qq123123",
# }
# a = requests.post(url="https://fv1.wlyuan.com/login", data=json.dumps(post_data))
# a = requests.post(url="http://192.168.1.52:7777/api/login", data=json.dumps(post_data))
# print(json.loads(a.content))

#
# a = requests.post(url="https://fv1.wlyuan.com/api/login", data=json.dumps(post_data))
# print(json.loads(a.content))
# #
# def get_basic_auth_str(username, password=''):
#     temp_str = username + ':' + password
#     # 转成bytes string
#     bytesString = temp_str.encode(encoding="utf-8")
#     # base64 编码
#     encodestr = base64.b64encode(bytesString)
#     # 解码
#     decodestr = base64.b64decode(encodestr)
#
#     return 'Basic ' + encodestr.decode()
#

# headers = {"Content-Type": "application/json;charset=UTF-8",
#            "Authorization": json.loads(a.content)['token']
#            }
# data = {'id': 24}
# data = {'id': 24,'area_id':10002,}
# data = {'area_id': 100011, 'sales_name': '测试1号', 'id': 24}

# data = {
#     'type': '7',
#     'User_name': 'admin',
#     'user_id': 23,
#     'page': 2,
#     'size': 2,
#     'datalist': [{'imei': '351608086033797', 'name': '伟盛货运',}, {'imei': '351608086039992', 'name': '伟盛货运',},
#                  {'imei': '351608086033540', 'name': '伟盛货运',}, {'imei': '351608086044257', 'name': '伟盛货运',}]
# }
# #

# data = {
#     "area_id":10002,
#     "id":"105"
# }
# data = {'area_id':10002,
#         'id':"23"}

# a = requests.post(url="http://192.168.1.52:7777/api/get_sales_tree/", data=json.dumps(data), headers=headers)
# print(json.loads(a.content))

# b = requests.post(url="http://192.168.1.52:7777/api/get_sales_tree/", data=json.dumps(data), headers=headers)
# print(json.loads(b.content))

# daa = {"user_id":"34","imei":"351608086029894","end_time":"2020-03-31 04:00:17"}
# a = requests.post(url="http://192.168.1.52:7777/renew_device/", data=json.dumps(daa), headers=headers)
# print(json.loads(a.content))
# a = requests.post(url="https://fv1.wlyuan.com/get_msg", data=json.dumps(post_data), headers=headers)


# print(json.loads(b.content))
# post_data = {
#     "username": 'test2',
#     "password": "123456",
#     "role_id":1,
#     "sales_name":"测试1号"
# }
#
# a = requests.post(url="http://192.168.1.52:7777/signin", data=json.dumps(post_data))
# print(json.loads(a.content))

# data = {
#     "role_id":1,
#     "username": 'test1',
#     "Company_Name": "test1",
#     "Sales_Company": "北京",
# }
# data = {
#     "role_id":1,
#     "page": 1,
#     "size": 20,
# }
#
# data = {
#     "role_id":1,
#     "user_id":25,
#     "page": 1,
#     "size": 20,
# }
# data = {
#     "username":'aaaaaaa',
#     "password":'aaa',
#     "role_id":1,
#     "sales_name":'aaa'
# }
# a = requests.post(url="http://192.168.1.52:7777/signin", data=json.dumps(data))
# print(json.loads(a.content))

# data = {
#     "page": 1,
#     "size": 20,
# }
# a = requests.post(url="http://192.168.1.52:7777/search_pactcode/", data=json.dumps(data))
#
# print(json.loads(a.content))
#


# data = [{"imei":"351608087065095"},{"imei":"351608087065418"},{"imei":"351608087058751"},{"imei":"351608087064312"},{"imei":"351608087086018"},{"imei":"351608087071911"},{"imei":"351608087065111"},{"imei":"351608087065400"},{"imei":"351608087065046"},{"imei":"351608087085846"},{"imei":"351608087064338"},{"imei":"351608087065053"},{"imei":"351608087065434"},{"imei":"351608087064395"},{"imei":"351608087065392"},{"imei":"351608086051203"},{"imei":"351608086051195"},{"imei":"351608086050858"},{"imei":"351608086051013"},{"imei":"351608086051021"}]
# dd = []
# for i in data:
#     dd.append(i['imei'])
#
# print(dd)
# print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# data = [{'imei': "351608081234567", 'user_name': "超级管理员"}, {'imei': "351608081234566", 'user_name': "超级管理员"},
#         {'imei': "351608081234565", 'user_name': "超级管理员"}, {'imei': "351608081234565", 'user_name': "超级管理员"}]
# data = {
#     'id': 84,
#     'imei': '351608081234569',
#     'is_disable': 0,
#     'remarks': '111111',
#     'user_id': '84'
# }
#
# a = requests.post(url="http://192.168.1.52:7777/api/set_disable_status/", data=json.dumps(data), headers=headers)

# print(json.loads(a.content))

# data= {"url":"https://qiye.wlyuan.com.cn/tms/fileupload/5.png","requestId":"ed194fb0982c3b20","verify":"b26dafaa97867faa0f0aa63fdeb26a28","telephoneNum":"18670090000"}
#
# /get_img/
#
# a = requests.post(url="http://192.168.1.52:7777/api/get_img/")
#
# print(json.loads(a.content))
data = [{'field': 111, 'title': 1}, {'field': 111, 'title': 1}, {'field': 111, 'title': 1},
        {'field': 111, 'title': 1}, {'field': 111, 'title': 1}, {'field': 111, 'title': 1},
        {'field': 111, 'title': 1}]
field = [{'field': 'field', 'title': '5'}, {'field': 2, 'title': '2'},
         {'field': 3, 'title': '3'}, {'field': 4, 'title': '4'},
         {'field': 5, 'title': '5'}, {'field': 6, 'title': '6'},
         {'field': 7, 'title': '7'}, {'field': 8, 'title': '8'}]


# @api.route("/exp_excel/",methods=['get'])
# def exp_excel():
#     # data = request.get_json(force=True)
#     # page = data['page']
#     # size = data['size']
#     data = {'page': 1, 'size': 10}
#     a = Set_Device_Comapy(data=data)
#     a = a.get_all_Device()
#     query_sets = a['datalist']
#     l =[]
#     count = 0
#     for i in query_sets:
#         count =count+1
#         l.append({'count':i})
#     return excel.make_response_from_array(l, 'xlsx',
#                                           sheet_name=1,
#                                           file_name=2)


# @api.route('/export_excel/', methods=['GET'])
# def export_excel():
#     excel_resp = make_excel_list()
#     return excel.make_response_from_array(excel_resp, 'xlsx',
#                                           sheet_name=1,
#                                           file_name=2)
#
# def make_excel_list():
#     list_data = []
#     data = {'page': 1, 'size': 10}
#     a = Set_Device_Comapy(data=data)
#     a = a.get_all_Device()
#     query_sets = a['datalist']
#     field = [x for x in query_sets[0].keys()]
#     name = [x for x in query_sets[0].keys()]
#     list_data.append(name)
#     for item in query_sets:
#         tmp = []
#         for fi in field:
#             if fi in item.keys():
#                 tmp.append(item[fi])
#             else:
#                 tmp.append('')
#         list_data.append(tmp)
#     return list_data
#
# app.register_blueprint(api, url_prefix='/api')

def make_excel_list(data, fields):
    list_data = []
    field = [x['field'] for x in fields]
    name = [x['title'] for x in fields]
    list_data.append(name)
    for item in data:
        tmp = []
        for fi in field:
            if fi in item.keys():
                print(fi)
                tmp.append(item[fi])
            else:
                tmp.append('')
        list_data.append(tmp)
    return list_data


a = make_excel_list(data=data, fields=field)
print(a)
'''@attention
    select
    d.Device_IMEICode as '设备编码',
	d.Device_PhoneNo as '设备号码',
	d.Device_SIMid as 'SIM提供商',
	d.Device_IMSI as 'IMSI码',
	d.Device_OwnerType as '是否自有',
	d.Device_Type as '设备类型',
	d.Device_temperature as '是否温控',
	d.Device_Invalid as '是否禁用' ,
	c.Company_Name as '客户名称',
  '最后承运商'=(
     select top 1 Index_SupplierName from TMS_OrderIndex  where d.Device_IMEICode=TMS_OrderIndex.Index_DeviceCode and Index_SrcClass = 2 order by TMS_OrderIndex.Index_CreateTime desc
   ) ,
'最后绑定时间'=(
     select top 1 Index_CreateTime from TMS_OrderIndex  where d.Device_IMEICode=TMS_OrderIndex.Index_DeviceCode and Index_SrcClass = 2 order by TMS_OrderIndex.Index_CreateTime desc
   ) 
   from TMS_Devices d,TMS_Company c where d.Device_CompanyID = c.Company_ID and d.Device_Invalid =0
    '''
