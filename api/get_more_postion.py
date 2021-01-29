import sys

sys.path.append("..")
from my_db.Models import Position
import time
import datetime
from mongoengine.queryset.visitor import Q


def local2utc(local_st):
    """本地时间转UTC时间（-8: 00）"""
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st


def get_Utc_time(t):
    a = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    o = datetime.timedelta(hours=8)
    return a + o


def get_location_time(t):
    a_t = t + datetime.timedelta(hours=8)
    l_t = a_t.strftime("%Y-%m-%d %H:%M:%S")
    return l_t


class More_Position:
    def __init__(self, data):
        self.data = data
        st = datetime.datetime.strptime(data['start_time'], "%Y-%m-%d %H:%M:%S")
        ed = datetime.datetime.strptime(data['end_time'], "%Y-%m-%d %H:%M:%S")
        self.st = local2utc(st)
        self.ed = local2utc(ed)

    def get_more_position(self):
        my_list = []
        if 'type' in self.data:
            p_type = self.data['type']
            res = Position.objects.filter(
                (Q(time__gte=self.st) & Q(time__lte=self.ed) & Q(type=int(p_type)) & Q(devId=str(self.data['imei'])))).order_by('time')
            for i in res:
                p_data = {
                    'devId': i.devId,
                    "longitude": i.longitude,
                    "latitude": i.latitude,
                    "bLongitude": i.bLongitude,
                    "bLatitude": i.bLatitude,
                    "type": i.type,
                    "time": get_location_time(i.time),
                    "speed": i.speed
                }
                my_list.append(p_data)
        else:
            res = Position.objects.filter(
                (Q(time__gte=self.st) & Q(time__lte=self.ed) & Q(devId=str(self.data['imei'])))).order_by('time')
            for i in res:
                p_data = {
                    'devId': i.devId,
                    "longitude": i.longitude,
                    "latitude": i.latitude,
                    "bLongitude": i.bLongitude,
                    "bLatitude": i.bLatitude,
                    "type": i.type,
                    "time": get_location_time(i.time),
                    "speed": i.speed
                }
                my_list.append(p_data)
        return my_list

    def get_new_position(self):
        res = Position.objects.filter(devId=str(self.data['imei'])).order_by('-time').limit(1)
        for i in res:
            return get_Utc_time(str(i.time))

    def get_test_position(self):
        my_list = []
        res = Position.objects.filter(
                (Q(time__gte=self.st) & Q(time__lte=self.ed) & Q(devId=str(self.data['imei'])))).limit(50)
        if res:
            for i in res:
                p_data = {
                    'devId': i.devId,
                    "longitude": i.longitude,
                    "latitude": i.latitude,
                    "bLongitude": i.bLongitude,
                    "bLatitude": i.bLatitude,
                    "type": i.type,
                    "time": get_location_time(i.time),
                    "speed": i.speed
                }
                my_list.append(p_data)
            return my_list
        else:
            return '暂无数据！'
# data = {
#     'imei': '351608087081225',
#     'start_time': '2019-05-15 00:00:00',
#     'end_time': '2019-06-15 00:00:00',
#     'type':2
# }
# p = More_Position(data)
# a = p.get_more_position()
# print(a)
