import os

proDir = os.path.split(os.path.realpath(__file__))[0]
configPath = os.path.join(proDir, "api")
path = os.path.abspath(configPath)
print(path)
from geopy.distance import geodesic

# d = geodesic((31.63128137579276, 120.23107581534349), (31.087546, 120.691985)).km
# print(d)
#
# 120.23107581534349, 31.63128137579276
#
# d = geodesic((31.63128137579276, 120.23107581534349), (31.323020545404689, 120.98705239267579)).km
# print(d)

d = geodesic((28.212183, 112.877473), (28.241488836472607, 112.93744764409886)).km
print(d)

# TMSDevice最新数据时间为2021-01-04 05:07:36. 当前扫描时间为2021-01-04 05:07:35.400546
