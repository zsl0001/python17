import requests
import json
# def add():
#     post_data={
#         "size":"20",
#         "page":"1"
#     }
#     res=requests.get(url="http://192.168.1.89:7777/Get_Device_Count/?size=20&page=1")
#     print(res.text)
#
# add()
# #{
#     "imei":["351608087081225","351608085028046","351608086050445"]
# # }
# headers = {"Content-Type":"application/x-www-form-urlencoded"}
#
# #bb
# post_data =[
#     {"imei":"351608087081225"}
# ]
# print(json.dumps(post_data))
# b = requests.post(url ="http://192.168.1.52:7777/Get_last_postion/",data=json.dumps(post_data))
# print(b.text)
# print(json.loads(b.text))
# # #
#
# post_data =[
#     {"name":"北京中联承达物流有限公司"}
# ]
# # print(json.dumps(post_data))
# a = requests.post(url ="http://192.168.1.52:7777/find_device_to_company_name/",data=json.dumps(post_data))
# print(a.text)
#
#

# 北京中联承达物流有限公司
# post_data =[
#     {"sales_name":'直销'},
# ]
#
# post_data1 =[
#     {"Company_Id":'189'},
# ]


# post_data =[
#     {"imei":'351608086050445'},
#     {"start_time": "2019-06-12 01:11:11"},
#     {"end_Time": "2019-06-12 10:11:11"}
# ]


# a = requests.post(url ="http://192.168.1.52:7777/Get_Company_Name/",data=json.dumps(post_data))
# print(a.text)

# a = requests.post(url ="http://192.168.1.52:7777/Get_Company_Device/",data=json.dumps(post_data1))
# print(a.text)
# print(type(a.text))
# c = json.loads(a.text)
# for i in c:
#     print(i)

# url = 'http://192.168.1.52:7777/Get_Sales_List/'
#
# a = requests.get(url ="http://192.168.1.52:7777/Get_Sales_List/")
# print(a.text)

# for i in post_data:
#     print(len(str(i["imei"])))
# post_data =[
#     {"imei":351608087081225},
#     {"name":"北京中联承达物流有限公司"}
# ]
#
#
# print(type(post_data[0]['imei']))



#imei='',start_time='2019-04-21 01:11:11',end_Time='2019-11-21 23:59:59'


#/http://192.168.1.52:7777/Get_more_postion/?imei=1351608086050445&start_time=2019-04-21 01:11:11&start_time=2019-11-21 23:59:59/
#Company_Name = '上海中保物流有限公司',Index_PactCode = "RLN190122046"

# post_data =[
#     {"Company_Name":"上海中保物流有限公司"},
#     {"Index_PactCode":"RLN190122046"}
# ]
#  # 通过公司名字和合同号 获取短信详情
# a = requests.post(url ="http://192.168.1.52:7777/get_msg/",data=json.dumps(post_data))
# print(a.text)



# post_data =[
#     {"imei":351608085005465},
#     {"page":1},
#     {"size":20}
# ]
# # 通过设备码获取合同号
# a = requests.post(url ="http://192.168.1.52:7777/get_pactcode/",data=json.dumps(post_data))
# print(a.text)


# post_data =[
#     {"imei":351608086029910},
#     {'start_time':'2019-11-15 05:05:28'},
#     {"end_Time":'2019-11-21 03:31:23'},
#     {"page":1},
#     {"size":20}
# ]
# # 通过设备码获取合同号
# a = requests.post(url ="http://192.168.1.52:7777/get_more_sleepNotice/",data=json.dumps(post_data))
# print(a.text)
# post_data =[
#     {"imei":351608086029910},
# ]
# # 通过设备码获取合同号
# a = requests.post(url ="http://192.168.1.52:7777/get_last_sleepNotice/",data=json.dumps(post_data))
# print(a.text)


post_data =[
    {"sales_company":'长沙'},
]
# 通过设备码获取合同号
a = requests.post(url ="http://192.168.1.52:7777/Get_List/",data=json.dumps(post_data),)
print(a.text.encode('utf-8').decode('unicode_escape'))