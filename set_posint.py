'''http://139.196.160.63:8077/Get_order/351608086050619/955867/post123/'''
"""http://139.196.160.63:1222/setting/charge/351608086041071/4/360/955867"""


import requests
import time
def set_pos(path):
    imei_path = path + '\\imei.txt'
    with open(imei_path, "r+",encoding='UTF-8') as f:
        data = f.read().splitlines()
    succ_imei = path + '\\imei3.txt'
    with open(succ_imei, "r+", encoding='UTF-8') as f:
        data2 = f.read().splitlines()

    url = 'http://139.196.160.63:1222/setting/charge/'
    typ ='/4/'
    init = '3600/'
    tag = '956867'
    for i in data:
        if i not in data2:
            set_url = url + i +typ + init +tag
            res = requests.get(set_url)
    time.sleep(5)
    for i in data:
        if i not in data2:
            url = "http://139.196.160.63:8077/Get_order/{}/956867/post123/".format(i)
            re = requests.get(url)
            if re.text == '修改成功':
                print(i, re.text)
                with open(succ_imei, "a+", encoding='UTF-8') as f:
                    f.write(i +'\n')


while 1:
    set_pos(r'D:\PycharmProjects\python17\api_preceipt\my_db')
    time.sleep(3600)