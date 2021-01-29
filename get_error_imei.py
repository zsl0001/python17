import os
import sys

sys.path.append("..")
import pymssql
import re
import json

conn = pymssql.connect(host='172.16.16.23', user='WLY', password='Wly2.techns@907', database='WLY', charset='utf8')
# 使用cursor方法创建一个游标
cursor = conn.cursor(as_dict=True)

my_path = os.path.abspath(os.curdir)
imei_path = os.path.join(my_path, 'imei')
imei_path2 = os.path.join(my_path, 'imei2')
imei_list = []
with open(imei_path, 'r') as f:
    for i in f:
        imei_list.append(i.strip('\n'))
sql = "SELECT Device_IMEICode from TMS_Devices where Device_Type = 3 AND Device_Invalid = 0"
cursor.execute(sql)
results = cursor
l = []
for i in results:
    l.append(i['Device_IMEICode'])
for i in l:
    if i not in imei_list:
        with open(imei_path2, 'a+') as f:
            f.write(i + '\n')
