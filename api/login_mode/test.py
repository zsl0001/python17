import requests
import json

post_data={
    "username":'admin',
    "password":"123456",
}
# a = requests.post(url="http://192.168.1.52:5555/signin",data=json.dumps(post_data))
# print(a.text.encode('utf-8').decode('unicode_escape'))


a = requests.post(url="http://192.168.1.52:7777/login",data=json.dumps(post_data))
print(a.text.encode('utf-8').decode('unicode_escape'))


a = requests.get(url="http://192.168.1.52:7777/")
print(a.text.encode('utf-8').decode('unicode_escape'))
