from socket import *

HOST = ''
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

s = socket(AF_INET, SOCK_STREAM)
s.bind(ADDR)
s.listen(5)

while True:
    print('等待连接。。。')
    c, addr = s.accept()
    while True:
        data = c.recv(BUFSIZ)
        print(data)
s.close()


import stomp

listener_name = 'SampleListener'
# 推送到主题
__topic_name1 = '/queue/INFO_TO_CUS	'
__host = '122.51.209.32'
__port = 61613
__user = 'admin'
__password = 'admin'


class SampleListener():
    def on_message(self, message):
        print('message: %s' % message)


mq_conn = stomp.Connection10([(__host, __port)], auto_content_length=False)
mq_conn.set_listener(listener_name, SampleListener())
mq_conn.start()
mq_conn.connect(__user, __password, wait=True)
mq_conn.subscribe(__topic_name1)
mq_conn.disconnect()