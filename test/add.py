import random
import sys

sys.path.append("..")
from my_db.Models import Position, Status
import datetime

startTime = '2020-09-14 01:00:00'
startTime1 = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
startTime2 = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
# s = startTime + datetime.timedelta(minutes=1)
s_lng = 102.098796
s_lat = 36.506891
s_blng = 102.107328
s_blat = 36.5131542
numbers = [0, 2]
model = 0
mcc = 0
mnc = 0
lac = 0
lithium = 60
gsmLevel = 100
charging = 0
light = 1
devId = '351608086209015'
count = 0
p = Position()
S = Status()
while count < 10000:
    count = count + 1
    type = random.sample(numbers, 1)
    speed = random.randint(0, 100)
    temperature = random.randint(200, 300)
    humidity = random.randint(500, 700)
    course = random.randint(0, 360)
    startTime1 = startTime1 + datetime.timedelta(minutes=1)
    startTime2 = startTime2 + datetime.timedelta(minutes=2)
    p.devId = devId
    p.longitude = s_lng + 0.01
    p.latitude = s_lat + 0.01
    p.bLongitude = s_blng +0.01
    p.bLatitude = s_blat +0.01
    p.model = model
    p.type = type[0]
    p.mcc = mcc
    p.mnc =mnc
    p.lac = lac
    p.time = startTime1
    p.course = course
    p.speed = speed
    p.save()
    S.devId = devId
    S.lithium = lithium
    S.gsmLevel = gsmLevel
    S.charging = charging
    S.temperature = temperature
    S.humidity = humidity
    S.date = startTime2
    S.save()
    print(count,startTime2)