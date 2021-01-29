# import os
# os.system('ls')
# os.system('docker restart myredis')
import datetime

a = "2020-12-19 10:43:10.732550"
b = "2020-12-19 10:43:18"

a1 = datetime.datetime.strptime(a, "%Y-%m-%d %H:%M:%S.%f")
b1 = datetime.datetime.strptime(b, "%Y-%m-%d %H:%M:%S")
print((a1-b1).seconds)
print((b1-a1).seconds)

print(a1.minute)
print(b1.minute)

