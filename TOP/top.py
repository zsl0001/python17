import sys

from mongoengine import Q

sys.path.append("..")

import datetime

from my_db.Models import Log


def get_now_time(t):
    a = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    o = datetime.timedelta(hours=8)
    return a + o


arr_time = datetime.datetime.now()
with open('imei.txt') as f:
    a = f.read()
    a = a.split('\n')
for i in a:
    res = Log.objects.filter(imei=str(i)).order_by('-time').first()
    if res:
        elc = str(res.content).split(',')[2]
        elc_time = get_now_time(str(res.time).split('.')[0])
        a_s = (arr_time - elc_time).seconds
        print(i,elc,a_s,'正常')
        if int(elc) > 20 and a_s > 3600:
            print(i, elc, a_s,'不正常')

# res = Log.objects.filter(imei='351608087084708').order_by('time').first()

