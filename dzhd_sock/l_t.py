import time
import binascii
import random
# from socket import socket, AF_INET, SOCK_STREAM
import socket
from locust import Locust, TaskSet, events, task


class TcpSocketClient(socket.socket):

    def __init__(self, af_inet, socket_type):
        super(TcpSocketClient, self).__init__(af_inet, socket_type)

    def connect(self, addr):
        start_time = time.time()
        try:
            super(TcpSocketClient, self).connect(addr)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="tcpsocket", name="connect", response_time=total_time, exception=e,
                                        response_length=0
                                        )
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="tcpsocket", name="connect", response_time=total_time,
                                        response_length=0)

    def send(self, msg):
        start_time = time.time()
        try:
            super(TcpSocketClient, self).send(msg)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="tcpsocket", name="send", response_time=total_time, exception=e,
                                        response_length=0
                                        )
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="tcpsocket", name="send", response_time=total_time,
                                        response_length=0)

    def recv(self, bufsize):
        recv_data = ''
        start_time = time.time()
        try:
            recv_data = super(TcpSocketClient, self).recv(bufsize)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="tcpsocket", name="recv", response_time=total_time, exception=e,
                                        response_length=0
                                        )
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="tcpsocket", name="recv", response_time=total_time,
                                        response_length=0)
        return recv_data


class TcpSocketLocust(Locust):
    """
    This is the abstract Locust class which should be subclassed. It provides an TCP socket client
    that can be used to make TCP socket requests that will be tracked in Locust's statistics.
    """

    def __init__(self, *args, **kwargs):
        super(TcpSocketLocust, self).__init__(*args, **kwargs)
        self.client = TcpSocketClient(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = (self.host, self.port)
        self.client.connect(ADDR)


meg2 = '5602070005140C1B0E353855302C32393630312C34333039322C317C302C32393630312C373635322C337C302C32393630312C373635322C337C302C32393630312C373635322C327C302C302C302C307C302C302C302C307C302C302C302C307CF3E00D0A'
meg3 = '56020100045801955F302C32393630312C34333039322C317C302C32393630312C373635322C337C302C32393630312C373635322C337C302C32393630312C373635322C327C302C302C302C307C302C302C302C307C302C302C302C307C463E0D0A'


class TcpTestUser(TcpSocketLocust):
    host = "192.168.1.45"
    port = 8306
    min_wait = 100
    max_wait = 1000

    class task_set(TaskSet):
        @task
        def send_data(self):
            meg = '787811010351608085{}101832000001F0870D0A'.format(random.randint(100000, 999999))
            print(meg)
            senddata = binascii.a2b_hex(meg)
            self.client.send(senddata)
            # data = self.client.recv(2048)
            meg2 = '78782222140C1B053510CB0306E55F0C1C5B8E0A154C01CC00287D001FB8010600000204C60D0A'
            senddata2 = binascii.a2b_hex(meg2)
            self.client.send(senddata2)
            # data2 = self.client.recv(2048)
            # print(data2)
            meg3 = '78780A13400604000100046A6B0D0A'
            senddata3 = binascii.a2b_hex(meg3)
            self.client.send(senddata3)
            # data = self.client.recv(2048)
            # print(data)

        # @task
        # def send_data(self):
        #     meg = '78782222140C1B053510CB0306E55F0C1C5B8E0A154C01CC00287D001FB8010600000204C60D0A'
        #     senddata = binascii.a2b_hex(meg)
        #     self.client.send(senddata)
        #     data = self.client.recv(2048)
        #     print(data)
        #
        # @task
        # def send_data(self):
        #     meg = '78780A13400604000100046A6B0D0A'
        #     senddata = binascii.a2b_hex(meg)
        #     self.client.send(senddata)
        #     data = self.client.recv(2048)
        #     print(data)


if __name__ == "__main__":
    user = TcpTestUser()
    user.run()
