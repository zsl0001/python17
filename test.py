import requests
import json

# header = {
#     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     'Cookie': '__cfduid=d42851f6479480a9f18740788571439651599699837; ct_winduser=eyJpdiI6IldSclNFNFRKSGk5MlNmOHRzZ0NPK2c9PSIsInZhbHVlIjoidHJHWjRmSlF2dDBLZDkxTVJKZEh0ckJ1bG93QnVqN3E0YlwvMnJ6SVV5NnNUMzBDdlozQkd0NHR5THFIYU10UTJEUThQMjJqd050QzZQYllKZTZIWkRzaFBQSjg2NklmOWRad0l2Rm1WUk83TmZUbDVFNERVNTdsTWNjT0ZYVHJxIiwibWFjIjoiNTBkZjBjZmMzNTg2ODA0ZTgxNWE2YWU0MzUyMGIxNWZmMjk5YmIzODQzYmFhOWExNWIwMzQxM2M2N2RkNTNhZiJ9; XSRF-TOKEN=eyJpdiI6ImFkSkxtemtvU1pvb2hDXC9mUUhGNWFBPT0iLCJ2YWx1ZSI6InhTejJQT3prM3RWbnBZaHZyeXVEVjZmVVdrUGZiOVNzcUVlWFdmNmtSZTZXSjNGS1BlRHZ2d2VQR1hrM2ZzelhIWDM3OG5WME42R3EybWdoWW0rcGp3PT0iLCJtYWMiOiI3ZTU4NTc5NzU1MjUxMzQwMGNkYTRlNTMyM2IxMmNkYWQzYjY2MDBkYjQ1NzcxZmNmMTA4NjcwMTFmMGE1MTExIn0%3D; laravel_session=eyJpdiI6IllxTlE2UHorWXdoS3FuVUpJbmlQM0E9PSIsInZhbHVlIjoiVjRjZ1A1eTBUTHI5UDJ2RWJvR3hCVWg3Y0pNd3BiUXhBS055bjBcLzg4bWRhVkdDWlZ3YXV0cklEUFkwbjVjYWRwMHlLanpPK0xJWllkWUVxS2JadGVBPT0iLCJtYWMiOiIwYzMyYWU1YTNlYjkzN2QyMTlmODA4MTY0ZTZmNjIxODM3NDY4ZmFmMTZiNmU2MTQ1ZTI4NDczNjQzMTRmMzU0In0%3D',
#     'X-Requested-With': "XMLHttpRequest"
# }
# data = {'_token': 'DrMJniuo31HoigHrY7EA7UD6ywr9jXLq0udPiQS5',
#         'keytype': 'advanced',
#         'type': 'create',
#         'quantity': 1,
#         'iskey': 'null',
#         'appName': 2,
#         'verifyid': 179867
#         }
# url = 'http://cn.cyber-tank.com/keys?tabs=keys'
# data = {"imeicode": "351608086100000"}
#
# dat = {"user_id":"84","password":"p123456","is_disable":0,"type":1,"role_id":1,"id":"84","username":"超级管理员","useraccount":"admin"}
# url = 'https://fv1.wlyuan.com/api/set_account_properties'
# res = requests.post(url=url, data=json.dumps(dat))
# print(res.text)
my_filters = {'Index_PactCode': '4500299166'}
for attr,value in my_filters.items():
    print(value)