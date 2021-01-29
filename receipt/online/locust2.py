import time

import requests
from locust import HttpLocust, TaskSet, task
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json


class my_re(TaskSet):

    @task(1)
    def add_order(self):

        headers = {'Accept': 'application/json, text/plain, */*',
                   'Content-Type': 'application/json;charset=UTF-8',
                   'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNjI5OTIiLCJ1c2VyQ29tcGFueU5hbWUiOiLljJfkuqzlsI_onJzonILlqZrlp7vmnI3liqHmnInpmZDlhazlj7jnu7XpmLPliIblhazlj7giLCJyb2xlSWRzIjoiNTEyLDEyOCwzMiw4LDIsMSIsInVzZXJDb21wYW55aWQiOjMxNTA1LCJ1c2VyUGhvbmUiOiIxODY3MDA5MDM1NiIsIm1vZHVsZSI6InFpeWUiLCJpc3MiOiJ3bHl1YW4iLCJ1c2VyTmFtZSI6IueOi-Wul-awuCIsImV4cCI6MTYxMTY0MDc2OCwidXNlckNvZGUiOiIifQ.LYFmTsYJ_lFh5QnbhN2xkpeEkyPfRZbghAcwOODbMTM'}
        res = self.client.post(headers=headers, data=json.dumps(data),
                               url='/order/createOrder')
        time.sleep(1)
        print(res.text)


class websitUser(HttpLocust):
    task_set = my_re
    host = "http://192.168.1.89:1256/tms"
    min_wait = 3000  # 单位为毫秒
    max_wait = 6000  # 单位为毫秒m
