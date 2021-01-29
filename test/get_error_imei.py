import os
import sys

sys.path.append("..")
import pymyssql
import re
import json

conn = pymyssql.connect(host='122.51.209.32', port=3306, user='root', passwd='123456', db='acctop', charset='utf8')
# 使用cursor方法创建一个游标
cursor = conn.cursor(cursor=pymyssql.cursors.DictCursor)

my_path = os.path.abspath(os.curdir)
imei_path = os.path.join(my_path, 'imei')
imei_list = []
with open(imei_path, 'r') as f:
    for i in f:
        imei_list.append(i.strip('\n'))
