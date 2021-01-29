import sys
import time

sys.path.append("..")
import datetime
import requests
from models import db, TMSOrderIndex, TMSDevice


def db_electric():
    arr_time = datetime.datetime.now()
    res3 = db.session.query(TMSDevice.Device_PositionTime, TMSDevice.Device_IMEICode).filter(
        TMSDevice.Device_Invalid == 0,
        TMSDevice.Device_Type == 3).order_by(
        TMSDevice.Device_PositionTime.desc()).first()
    res2 = db.session.query(TMSDevice.Device_PositionTime).filter(TMSDevice.Device_Invalid == 0,
                                                                  TMSDevice.Device_Type == 2).order_by(
        TMSDevice.Device_PositionTime.desc()).first()

    da = res3[0]
    print('TMSDevice3代设备最新数据时间为{}.'.format(da), '当前扫描时间为{}'.format(arr_time))
    a_s = (arr_time.minute - da.minute)
    print(arr_time.minute, da.minute)
    if a_s >= 5:
        url = 'https://oapi.dingtalk.com/robot/send?access_token=8bd654391d651af3f5f8592580c71899ae3c9ff22cf98e171fe08483ed728608'
        content = {
            "msgtype": "text",
            "text": {
                "content": "3代设备定位超过5分钟未更新，请检查服务是否正常"
            },
            "at": {
                "isAtAll": True
            }
        }
        headers = {"Content-Type": "application/json;charset=utf-8"}
        r = requests.post(url=url, headers=headers, json=content)
        print(r.content)
    da2 = res2[0]
    print('TMSDevice2代最新数据时间为{}.'.format(da2), '当前扫描时间为{}'.format(arr_time))
    a_s2 = (arr_time.minute - da2.minute)
    print(arr_time.minute, da2.minute)
    if a_s2 >= 5:
        url = 'https://oapi.dingtalk.com/robot/send?access_token=8bd654391d651af3f5f8592580c71899ae3c9ff22cf98e171fe08483ed728608'
        content = {
            "msgtype": "text",
            "text": {
                "content": "2代设备定位超过5分钟未更新，请检查服务是否正常"
            },
            "at": {
                "isAtAll": True
            }
        }
        headers = {"Content-Type": "application/json;charset=utf-8"}
        r = requests.post(url=url, headers=headers, json=content)
        print(r.content)
        print(11111)


while 1:
    db_electric()
    time.sleep(300)