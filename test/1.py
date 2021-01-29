# import requests
# import json
# 
# 
# 
# data = {'dddddd':'wwww'}
# url = ' http://192.168.1.52:6666/aotu_send_msg/'
# data = json.dumps(data)
# res = requests.post(url,data)

import re

a = re.match(r'1[3,4,5,7,8]\d{9}', '18670090356')

print(a, len('18670090356'))
