import sys
import time

sys.path.append("..")

from socket import *
import binascii

from models import db, TMSOrderIndex, TMSDevice
import datetime

# 2353
arr_time = datetime.date.today()
star_time = arr_time - datetime.timedelta(days=3)
res = db.session.query(TMSOrderIndex.Index_DeviceCode).filter(TMSOrderIndex.Index_CreatorCompanyID == '2353',
                                                              TMSOrderIndex.Index_Status == 2,
                                                              TMSOrderIndex.Index_DeviceCode >= '35160808',
                                                              TMSOrderIndex.Index_FromTime >= star_time).all()
l = []
for i in res:
    l.append(i[0])
l2 = list(set(l))


def main():
    print("开始处理{}".format(datetime.datetime.now()))
    # 1.创建tcp_client_socket 套接字对象
    # 55022f010351608087072570000512340d0a
    tcp_client_socket = socket(AF_INET, SOCK_STREAM)
    # 作为客户端，主动连接服务器较多，一般不需要绑定端口
    # 2.连接服务器
    tcp_client_socket.connect(("106.14.17.10", 8306))
    for k in l2:  # 351608087072570
        meg = '55022f010{}000512340d0a'.format(k)
        print('正在设置{}'.format(k))
        senddata = binascii.a2b_hex(meg)
        tcp_client_socket.send(senddata)
        time.sleep(0.5)
    tcp_client_socket.close()
    print("处理完成{}".format(datetime.datetime.now()))


main()
# print('处理完成')
