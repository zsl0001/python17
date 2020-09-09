import sys

sys.path.append("..")
from concurrent.futures.thread import ThreadPoolExecutor
from mongoengine.queryset.visitor import Q
import requests
import datetime
import mongoengine
import json
from myconfig import mgdb, sqldb, api_cfg

con = mongoengine.connect(db=mgdb['db'], host=mgdb['host'])


def trans_add(lat, lng):
    base_url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=SMm8htpBXtu3Hd4n5XUsQwiUnMGvWdBU&output=json&coordtype=wgs84ll&location='
    location = str(lat) + ',' + str(lng)
    url = base_url + location + '&extensions_poi=1'
    res = requests.get(url)
    d = json.loads(res.text)
    try:
        addr = d['result']['formatted_address']
        pos = d['result']['pois'][0]
        adds_info = '距{}({})约{}米.'.format(pos['name'], pos['direction'], pos['distance'])
        ps = addr + ',' + adds_info
        return ps
    except Exception as e:
        print(e)
        return d


class Status(mongoengine.Document):
    meta = {
        'collection': 'status', 'strict': False
    }
    devId = mongoengine.StringField()
    date = mongoengine.DateTimeField()
    _class = mongoengine.StringField()
    lithium = mongoengine.IntField()
    gsmLevel = mongoengine.IntField()
    charging = mongoengine.IntField()


class ArriveMessage(mongoengine.Document):
    meta = {
        'collection': 'arriveMessage', 'strict': False
    }
    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    atime = mongoengine.DateTimeField()
    arrtime = mongoengine.DateTimeField()
    gpstime = mongoengine.DateTimeField()
    lng = mongoengine.FloatField()
    lat = mongoengine.FloatField()
    code = mongoengine.StringField()
    version = mongoengine.IntField()


class DevInfo(mongoengine.Document):
    meta = {
        'collection': 'devInfo', 'strict': False
    }

    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    status = mongoengine.DictField()
    tag = mongoengine.IntField()
    workMode = mongoengine.IntField()
    host = mongoengine.StringField()
    port = mongoengine.IntField()
    time2Sleep = mongoengine.IntField()
    posInvl = mongoengine.IntField()
    hbInvl = mongoengine.IntField()
    devId = mongoengine.StringField()


class EndedMessage(mongoengine.Document):
    meta = {
        'collection': 'endedMessage', 'strict': False
    }

    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    etime = mongoengine.DateTimeField()
    endtime = mongoengine.DateTimeField()
    gpstime = mongoengine.DateTimeField()
    code = mongoengine.StringField()
    lng = mongoengine.FloatField()
    lat = mongoengine.FloatField()
    version = mongoengine.IntField()


class OrderResult(mongoengine.Document):
    meta = {
        'collection': 'orderResult', 'strict': False
    }

    _id = mongoengine.StringField()
    devId = mongoengine.StringField()
    tag = mongoengine.IntField()
    date = mongoengine.DateTimeField()
    res = mongoengine.StringField()


class Position(mongoengine.Document):
    meta = {
        'collection': 'position', 'strict': False
    }
    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    devId = mongoengine.StringField()
    longitude = mongoengine.FloatField()
    latitude = mongoengine.FloatField()
    bLongitude = mongoengine.FloatField()
    bLatitude = mongoengine.FloatField()
    model = mongoengine.IntField()
    type = mongoengine.IntField()
    mcc = mongoengine.IntField()
    mnc = mongoengine.IntField()
    lac = mongoengine.IntField()
    cellId = mongoengine.IntField()
    time = mongoengine.DateTimeField()
    course = mongoengine.IntField()
    speed = mongoengine.FloatField()
    address = mongoengine.StringField()


class SleepNotice(mongoengine.Document):
    meta = {
        'collection': 'sleepNotice', 'strict': False
    }

    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    date = mongoengine.DateTimeField()
    res = mongoengine.BooleanField()
    tag = mongoengine.IntField()
    imei = mongoengine.StringField()


class SmsQueue(mongoengine.Document):
    meta = {
        'collection': 'smsQueue', 'strict': False
    }

    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    qtime = mongoengine.DateTimeField()
    code = mongoengine.StringField()
    content = mongoengine.StringField()
    msgtype = mongoengine.IntField()
    version = mongoengine.IntField()


class StartMessage(mongoengine.Document):
    meta = {
        'collection': 'startMessage', 'strict': False
    }

    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    stime = mongoengine.DateTimeField()
    startime = mongoengine.DateTimeField()
    gpstime = mongoengine.DateTimeField()
    code = mongoengine.StringField()
    lng = mongoengine.FloatField()
    lat = mongoengine.FloatField()
    version = mongoengine.IntField()


class Status(mongoengine.Document):
    meta = {
        'collection': 'status', 'strict': False
    }
    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    lithium = mongoengine.IntField()
    gsmLevel = mongoengine.IntField()
    charging = mongoengine.IntField()
    devId = mongoengine.StringField()
    date = mongoengine.DateTimeField()
    temperature = mongoengine.IntField()
    humidity = mongoengine.IntField()
    light = mongoengine.IntField()


class Log(mongoengine.Document):
    meta = {
        'collection': 'log', 'strict': False
    }
    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    time = mongoengine.DateTimeField()
    msgType = mongoengine.StringField()
    content = mongoengine.StringField()
    imei = mongoengine.StringField()


def get_location_time(t):
    t = t + +datetime.timedelta(hours=8)
    l_t = t.strftime("%Y-%m-%d %H:%M:%S")
    return t


def get_Utc_time(t):
    a = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    o = datetime.timedelta(hours=8)
    return a - o


def get_location_time2(t):
    t = t + +datetime.timedelta(hours=8)
    l_t = t.strftime("%Y-%m-%d %H:%M:%S")
    return l_t


def get_last_position(args):
    l = []
    for i in args:
        data = {"devId": i['imei'], "bLongitude": "", "bLatitude": "", "time": "", "speed": "", "addr": '', "type": ''}
        dat = Position.objects(devId=i['imei']).order_by('-time').limit(1)
        for i in dat:
            data["Longitude"] = i["longitude"]
            data["Latitude"] = i["latitude"]
            data["bLongitude"] = i["bLongitude"]
            data["bLatitude"] = i["bLatitude"]
            data["addr"] = trans_add(lat=i["latitude"], lng=i["longitude"])
            data["time"] = str(get_location_time(i["time"]))
            data["speed"] = i["speed"]
            data["type"] = i["type"]
            l.append(data.copy())
    return l


# def get_last_position(imei):
#     data = {"devId": imei, "bLongitude": "", "bLatitude": "", "time": "", "speed": "", "addr": "", 'lithium': -1,
#             'gsmLevel': -1, 'temperature': 'null'}
#     b = datetime.datetime.now()
#     dat = Position.objects(devId=imei).order_by('-time').limit(1)
#     for i in dat:
#         data["bLongitude"] = i["bLongitude"]
#         data["bLatitude"] = i["bLatitude"]
#         data["time"] = str(get_location_time(i["time"]))
#         data["speed"] = i["speed"]
#         data["addr"] = trans_add(i["bLatitude"], i["bLongitude"])
#     if imei[8] == '6':
#         st = Status.objects(devId=str(imei)).order_by('-date').limit(1)
#         if len(st) != 0:
#             for j in st:
#                 data['lithium'] = j.lithium
#                 data['gsmLevel'] = j.gsmLevel
#                 data['charging'] = j.charging
#                 data['temperature'] = j.temperature
#             if (b - get_location_time(j.date)).total_seconds() > 420:
#                 d = SleepNotice.objects(imei=str(j.devId)).order_by('-date').limit(1)
#                 if len(d) != 0:
#                     for m in d:
#                         if m.date > j.date:
#                             data['Device_Status'] = '休眠'
#                         else:
#                             data['Device_Status'] = '离线'
#                 else:
#                     data['Device_Status'] = '离线'
#             else:
#                 data['Device_Status'] = '在线'
#     if imei[8] == '7':
#         st = Log.objects(imei=str(imei)).order_by('-imei').limit(1)
#         if len(st) != 0:
#             for j in st:
#                 data['lithium'] = str(j.content).split(',')[-1]
#                 data['gsmLevel'] = str(j.content).split(',')[1]
#                 if (b - get_location_time(j.time)).total_seconds() > 420:
#                     d = SleepNotice.objects(imei=str(j.imei)).limit(1)
#                     if len(d) != 0:
#                         for m in d:
#                             if m.date > j.date:
#                                 data['Device_Status'] = '休眠'
#                             else:
#                                 data['Device_Status'] = '离线'
#                     else:
#                         data['Device_Status'] = '离线'
#                 else:
#
#                     data['Device_Status'] = '在线'
#             else:
#                 data['Device_Status'] = '离线'
#     return data

def get_elc_type3(imei, start, end, page, size):
    per_dat = {
        "count": '',
        "datalist": ''
    }
    elc = []
    data = {'lithium': '', 'time': ''}
    start = get_Utc_time(start)
    end = get_Utc_time(end)
    count = Status.objects.filter((Q(date__gte=start) & Q(date__lte=end) & Q(devId=imei))).count()
    elc_data = Status.objects.filter((Q(date__gte=start) & Q(date__lte=end) & Q(devId=imei)))[
               (page - 1) * size:(page * size)]
    for i in elc_data:
        data['lithium'] = i.lithium
        data['time'] = get_location_time2(i.date)
        elc.append(data.copy())
    per_dat["count"] = count
    per_dat["datalist"] = elc
    return per_dat


def get_elc_type2(imei, start, end, page, size):
    per_dat = {
        "count": '',
        "datalist": ''
    }
    elc = []
    data = {'lithium': '', 'time': ''}
    start = get_Utc_time(start)
    end = get_Utc_time(end)
    count = Log.objects.filter((Q(time__gte=start) & Q(time__lte=end) & Q(imei=imei))).count()
    elc_data = Log.objects.filter((Q(time__gte=start) & Q(time__lte=end) & Q(imei=imei)))[
               (page - 1) * size:(page * size)]
    for i in elc_data:
        data['lithium'] = str(i.content).split(',')[2]
        data['time'] = get_location_time2(i.time)
        elc.append(data.copy())
    per_dat["count"] = count
    per_dat["datalist"] = elc
    return per_dat


# a = get_elc_type3('351608086051062', '2019-03-03 00:00:00', '2019-03-25 00:00:00',page=1,size=20)
# print(a)


def get_msg_info(Company_name=None, Index_PactCode=None, Index_Code=None, Order_Status=None, CustomerSymbolName=None):
    start_res_data = {
        "send_time": "",
        "send_location": "",
        "sms_content": "【物流源】{}发给您的物流运单{}已发货，请使用电子回单编号{}或运单号在物流源公众号、微信小程序上查询货物的在途情况。",
        "type": 1  # startMessage
    }
    arriv_res_data = {
        "send_time": "",
        "send_location": "",
        "sms_content": "【物流源】您的物流运单{}来自{}预计将于{}后到达指定收货地址，请知悉。您的签收码是******，请妥善保管切勿泄露。",
        "type": 2  # arriveMessage
    }
    startswith = str(Company_name) + "|" + str(Index_PactCode)

    endwith = str(Index_PactCode) + "|" + str(Company_name)

    sms = SmsQueue.objects.filter(content__startswith=startswith)
    if len(sms) == 0:
        startswith = str(CustomerSymbolName) + "|" + str(Index_PactCode)
        sms = SmsQueue.objects.filter(content__startswith=startswith)
        if len(sms) == 0:
            start_res_data = []
    sms2 = SmsQueue.objects.filter(content__startswith=endwith)
    if len(sms2) == 0:
        endwith = str(Index_PactCode) + "|" + str(CustomerSymbolName)
        sms2 = SmsQueue.objects.filter(content__startswith=endwith)
        if len(sms2) == 0:
            arriv_res_data = []
    for s in sms:
        sms_start = StartMessage.objects(code=s.code)
        cont = s.content.split('|')
        start_res_data["sms_content"] = start_res_data["sms_content"].format(*cont)
        start_res_data["send_time"] = get_location_time(s.qtime).strftime("%Y-%m-%d %H:%M:%S")
        for k in sms_start:
            start_res_data["send_location"] = (k.lng, k.lat)
    for s2 in sms2:
        sms_end = ArriveMessage.objects(code=s2.code)
        cont = s2.content.split('|')
        arriv_res_data["sms_content"] = arriv_res_data["sms_content"].format(*cont)
        arriv_res_data["send_time"] = get_location_time(s2.qtime).strftime("%Y-%m-%d %H:%M:%S")
        for m in sms_end:
            arriv_res_data["send_location"] = (m.lng, m.lat)
    l = [start_res_data, arriv_res_data]
    con.disconnect
    return l


def get_last_position2(imei):
    data = {"devId": imei, "bLongitude": "", "bLatitude": "", "time": "", "speed": "", "addr": "", 'lithium': -1,
            'gsmLevel': -1, 'temperature': 'null', "Device_Status": "离线"}
    b = datetime.datetime.now()
    dat = Position.objects.filter(devId=imei).order_by('-time').first()
    if dat:
        data["bLongitude"] = dat["bLongitude"]
        data["bLatitude"] = dat["bLatitude"]
        data["time"] = str(get_location_time(dat["time"]))
        data["speed"] = dat["speed"]
        data["addr"] = trans_add(dat["bLatitude"], dat["bLongitude"])
    if imei[8] == '6':
        st = Status.objects.filter(devId=str(imei)).order_by('-date').first()
        if None != st:
            data['lithium'] = st["lithium"]
            data['gsmLevel'] = st["gsmLevel"]
            data['charging'] = st["charging"]
            data['temperature'] = st["temperature"]
            if (b - get_location_time(st["date"])).total_seconds() > 420:
                d = SleepNotice.objects.filter(imei=str(st.devId)).order_by('-date').first()
                if d:
                    if d['date'] > st['date']:
                        data['Device_Status'] = '休眠'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '离线'
            else:
                data['Device_Status'] = '在线'
    if imei[8] == '7':
        st = Log.objects.filter(imei=str(imei)).order_by('-time').first()
        if None != st:
            data['lithium'] = str(st['content']).split(',')[-1]
            data['gsmLevel'] = str(st['content']).split(',')[1]
            if (b - get_location_time(st["time"])).total_seconds() > 420:
                d = SleepNotice.objects.filter(imei=str(st['imei'])).order_by('-date').first()
                if d:
                    if d['date'] > st['date']:
                        data['Device_Status'] = '休眠'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '离线'
            else:
                data['Device_Status'] = '在线'
    con.disconnect
    return data


def get_last_position3(imei):
    m = []
    l = []
    for i in imei:
        m.append(i['imei'])
    data = {"devId": '', "bLongitude": "", "bLatitude": "", "time": "", "speed": "", "addr": "", 'lithium': -1,
            'gsmLevel': -1, 'temperature': 'null', "Device_Status": "离线"}
    b = datetime.datetime.now()
    a = Position._get_collection().aggregate([
        {
            "$match": {
                "devId": {
                    "$in": m
                },
            }
        },
        {
            "$group": {'_id': "$devId", "time": {'$first': "$time"}, "lng": {'$first': "$bLongitude"},
                       "lat": {'$first': "$bLatitude"}, "model": {'$first': "$model"}, "speed": {'$first': "$speed"}}
        },
        {"$sort": {'time': -1}}
    ])
    for dat in a:
        data["devId"] = dat['_id']
        data["bLongitude"] = dat['lng']
        data["bLatitude"] = dat["lat"]
        data["time"] = str(get_location_time(dat["time"]))
        data["speed"] = dat["speed"]
        data["addr"] = trans_add(dat["lat"], dat['lng'])
        if dat['_id'][8] == '6':
            st = Status.objects.filter(devId=str(dat['_id'])).order_by('-date').first()
            if None != st:
                data['lithium'] = st["lithium"]
                data['gsmLevel'] = st["gsmLevel"]
                data['charging'] = st["charging"]
                data['temperature'] = st["temperature"]
                if (b - get_location_time(st["date"])).total_seconds() > 420:
                    d = SleepNotice.objects.filter(imei=str(dat['_id'])).order_by('-date').first()
                    if d:
                        if d['date'] > st['date']:
                            data['Device_Status'] = '休眠'
                        else:
                            data['Device_Status'] = '离线'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '在线'
        if dat['_id'][8] == '7':
            st = Log.objects.filter(imei=str(dat['_id'])).order_by('-time').first()
            if None != st:
                data['lithium'] = str(st['content']).split(',')[-1]
                data['gsmLevel'] = str(st['content']).split(',')[1]
                if (b - get_location_time(st["time"])).total_seconds() > 420:
                    d = SleepNotice.objects.filter(imei=str(dat['_id'])).order_by('-date').first()
                    if d:
                        if d['date'] > st['date']:
                            data['Device_Status'] = '休眠'
                        else:
                            data['Device_Status'] = '离线'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '在线'
        l.append(data.copy())
    con.disconnect
    return l


def get_devices_info(imei):
    l = []
    b = datetime.datetime.now()
    for i in imei:
        data = {"devId": '', "time": "", 'lithium': -1, 'gsmLevel': -1, 'temperature': 'null', "Device_Status": "离线"}
        imei = str(i['imei'])
        data['devId'] = imei
        if imei[8] == '6':
            st = Status.objects.filter(devId=str(imei)).order_by('-date').first()
            if None != st:
                data['lithium'] = st["lithium"]
                data['gsmLevel'] = st["gsmLevel"]
                data['charging'] = st["charging"]
                data['time'] = st["date"].strftime('%Y-%m-%d %H:%M:%S')
                data['temperature'] = st["temperature"]
                if (b - get_location_time(st["date"])).total_seconds() > 420:
                    d = SleepNotice.objects.filter(imei=str(imei)).order_by('-date').first()
                    if d:
                        if d['date'] > st['date']:
                            data['Device_Status'] = '休眠'
                        else:
                            data['Device_Status'] = '离线'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '在线'
        if imei[8] == '7':
            st = Log.objects.filter(imei=str(imei)).order_by('-time').first()
            if None != st:
                data['lithium'] = str(st['content']).split(',')[-1]
                data['gsmLevel'] = str(st['content']).split(',')[1]
                data['time'] = st["time"].strftime('%Y-%m-%d %H:%M:%S')
                if (b - get_location_time(st["time"])).total_seconds() > 420:
                    d = SleepNotice.objects.filter(imei=str(imei)).order_by('-date').first()
                    if d:
                        if d['date'] > st['date']:
                            data['Device_Status'] = '休眠'
                        else:
                            data['Device_Status'] = '离线'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '在线'
        l.append(data.copy())
    con.disconnect
    return l


def get_devices_info2(imei):
    l = []
    b = datetime.datetime.now()
    a = Status._get_collection().aggregate([
        {
            "$match": {
                "devId": {
                    "$in": m
                },
            }
        },
        {
            "$group": {'_id': "$devId", "time": {'$first': "$time"}, "lng": {'$first': "$bLongitude"},
                       "lat": {'$first': "$bLatitude"}, "model": {'$first': "$model"}, "speed": {'$first': "$speed"}}
        },
        {"$sort": {'time': -1}}
    ])
    for i in imei:
        data = {"devId": '', "time": "", 'lithium': -1, 'gsmLevel': -1, 'temperature': 'null', "Device_Status": "离线"}
        imei = str(i['imei'])
        data['devId'] = imei
        if imei[8] == '6':
            st = Status.objects.filter(devId=str(imei)).order_by('-date').first()
            if None != st:
                data['lithium'] = st["lithium"]
                data['gsmLevel'] = st["gsmLevel"]
                data['charging'] = st["charging"]
                data['time'] = st["date"].strftime('%Y-%m-%d %H:%M:%S')
                data['temperature'] = st["temperature"]
                if (b - get_location_time(st["date"])).total_seconds() > 420:
                    d = SleepNotice.objects.filter(imei=str(imei)).order_by('-date').first()
                    if d:
                        if d['date'] > st['date']:
                            data['Device_Status'] = '休眠'
                        else:
                            data['Device_Status'] = '离线'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '在线'
        if imei[8] == '7':
            st = Log.objects.filter(imei=str(imei)).order_by('-time').first()
            if None != st:
                data['lithium'] = str(st['content']).split(',')[-1]
                data['gsmLevel'] = str(st['content']).split(',')[1]
                data['time'] = st["time"].strftime('%Y-%m-%d %H:%M:%S')
                if (b - get_location_time(st["time"])).total_seconds() > 420:
                    d = SleepNotice.objects.filter(imei=str(imei)).order_by('-date').first()
                    if d:
                        if d['date'] > st['date']:
                            data['Device_Status'] = '休眠'
                        else:
                            data['Device_Status'] = '离线'
                    else:
                        data['Device_Status'] = '离线'
                else:
                    data['Device_Status'] = '在线'
        l.append(data.copy())
    con.disconnect
    return l


def distinguish_devices_type(data):  # 区分设备类型
    type2 = []  # 2代设备
    type3 = []  # 3代设备
    for i in data:
        if str(i['imei'])[8] == '6':
            type3.append(str(i['imei']))
        else:
            type2.append(str(i['imei']))
    return type2, type3


def get_type2_info(type2):
    l = []
    b = datetime.datetime.now()
    a = Log._get_collection().aggregate([
        {
            "$match": {
                "imei": {
                    "$in": type2
                },
            }
        },
        {
            "$group": {'_id': "$imei", "time": {'$max': "$time"}, "content": {'$first': "$content"}}
        },
        {"$sort": {'time': -1}}
    ])
    for dat in a:
        data = {"devId": '', "time": "", "lithium": -1, 'gsmLevel': -1, "Device_Status": "离线"}
        data['lithium'] = str(dat['content']).split(',')[-1]
        data['devId'] = dat['_id']
        data['gsmLevel'] = str(dat['content']).split(',')[1]
        data['time'] = get_location_time(dat["time"]).strftime("%Y-%m-%d %H:%M:%S")
        if (b - get_location_time(dat["time"])).total_seconds() < 420:
            data['Device_Status'] = '在线'
        l.append(data.copy())
    con.disconnect
    return l


def get_type3_info(type3):
    l = []
    b = datetime.datetime.now()
    a = Status._get_collection().aggregate([
        {
            "$match": {
                "devId": {
                    "$in": type3
                },
            }
        },
        {
            "$group": {'_id': "$devId",
                       "time": {'$max': "$date"}, "lithium": {'$first': "$lithium"},
                       "gsmLevel": {'$first': "$gsmLevel"}, "temperature": {'$first': "temperature"},
                       "charging": {'$first': "$charging"}}
        },
        {"$sort": {'time': -1}}
    ])
    for dat in a:
        data = {"devId": '', "time": ' ', 'lithium': -1, 'gsmLevel': -1, 'temperature': 'null', "Device_Status": "离线"}
        data['lithium'] = str(int(dat['lithium']))
        data['devId'] = dat['_id']
        data['gsmLevel'] = str(int(dat['gsmLevel']))
        data['time'] = get_location_time(dat["time"]).strftime("%Y-%m-%d %H:%M:%S")
        if dat['temperature'] != 'temperature':
            data['temperature'] = dat['temperature']
        if (b - get_location_time(dat["time"])).total_seconds() > 420:
            d = SleepNotice.objects.filter(imei=str(dat['_id'])).order_by('-date').first()
            if d:
                if d['date'] > dat['time']:
                    data['Device_Status'] = '休眠'
                else:
                    data['Device_Status'] = '离线'
            else:
                data['Device_Status'] = '离线'
        else:
            data['Device_Status'] = '在线'
        l.append(data.copy())
        con.disconnect
    return l


def get_devices_info3(type2, type3):  # 同步查询mongdb里二代和三代的设备信息
    with ThreadPoolExecutor(max_workers=5) as t:
        task1 = t.submit(get_type3_info, type3)
        task2 = t.submit(get_type2_info, type2)
    l1 = task1.result()
    l2 = task2.result()
    l = l1 + l2
    return l


def get_elc(imei):
    data = {'devId': '', 'lithium': '', 'time': '', 'gsmLevel': '', 'charging': '', 'temperature': '', 'humidity': '',
            'light': ''}
    elc_data = Status.objects.filter(devId=str(imei)).order_by('-date').first()
    if elc_data:
        data['devId'] = elc_data['devId']
        data['date'] = get_location_time2(elc_data['date'])
        data['lithium'] = elc_data['lithium']
        data['gsmLevel'] = elc_data['gsmLevel']
        data['charging'] = elc_data['charging']
        data['temperature'] = elc_data['temperature']
        data['humidity'] = elc_data['humidity']
        data['light'] = elc_data['light']
        return data
    else:
        return '暂无数据'


def get_order_res(imei, tag):
    elc_data = OrderResult.objects.filter(Q(tag=tag) & Q(devId=imei)).order_by('-date').first()
    if elc_data:
        return True
    else:
        return False


def get_test_last_position(imei):
    data = {"devId": imei, "bLongitude": "", "bLatitude": "", "time": "", "speed": "", "addr": '', "type": ''}
    dat = Position.objects(devId=imei).order_by('-time').limit(1)
    if dat:
        for i in dat:
            data["Longitude"] = i["longitude"]
            data["Latitude"] = i["latitude"]
            data["bLongitude"] = i["bLongitude"]
            data["bLatitude"] = i["bLatitude"]
            data["addr"] = trans_add(lat=i["latitude"], lng=i["longitude"])
            data["time"] = str(get_location_time(i["time"]))
            data["speed"] = i["speed"]
            data["type"] = i["type"]
        return data
    else:
        return '暂无数据！'


def get_info(imei, tag):
    elc_data = DevInfo.objects.filter(Q(tag=tag) & Q(devId=imei)).order_by('-status.date').first()
    data = {}
    if elc_data:
        data['devId'] = elc_data['devId']
        data['workMode'] = elc_data['workMode']
        data['date'] = str(get_location_time(elc_data['status']['date'])).split('.')[0]
        data['lithium'] = elc_data['status']['lithium']
        data['gsmLevel'] = elc_data['status']['gsmLevel']
        data['posInvl'] = elc_data['posInvl']
        data['time2Sleep'] = elc_data['time2Sleep']
        data['hbInvl'] = elc_data['hbInvl']
        data['host'] = elc_data['host']
        return data
    else:
        return '暂无数据！'


# get_info(imei='351608086050957', tag='959278204')
'''
db.getCollection("position").aggregate(
    [
        {
            "$match" : {
                "devId" : {
                    "$in" : ['351608087084708', '351608087065392', '351608087064395', '351608087065434', '351608087065053', '351608087064338', '351608087085846', '351608087065046', '351608087065400', '351608087065111', '351608087071911', '351608087086018', '351608087064312', '351608087058751', '351608087065418', '351608087084732', '351608087084443', '351608087084468', '351608087084484', '351608087084450', '351608087084435', '351608087084781', '351608087085994', '351608087060120', '351608087085929', '351608087062373', '351608087085903', '351608087061318', '351608087086091', '351608087070020', '351608087085978', '351608087065558', '351608087065731', '351608087065582', '351608087065533', '351608087065749', '351608087065574', '351608087070210', '351608087070194', '351608087064973', '351608087085879', '351608087070327', '351608087086059', '351608087060906', '351608087086067', '351608087059171', '351608086050825', '351608087065095', '351608087061508', '351608086051153', '351608087086083', '351608087085911', '351608087068131', '351608087085895', '351608087060682', '351608087059320', '351608087077694', '351608087062589', '351608087062399', '351608087061284', '351608087085986', '351608087073453', '351608087061730', '351608087076498', '351608087059023', '351608087084740', '351608086050734', '351608086050510', '351608086050809', '351608086050940', '351608086051161', '351608086051120', '351608086051187', '351608086050882', '351608086050551', '351608086050866', '351608086050569', '351608086050593', '351608086050767', '351608086050452', '351608086051005', '351608086050775', '351608086051179', '351608086050536', '351608086050874', '351608086050411', '351608086050577', '351608086051021', '351608086051013', '351608086050858', '351608086051195', '351608086051203', '351608087058199', '351608087058215', '351608087070640', '351608087080359', '351608087080326', '351608087059940', '351608087084773', '351608087064908', '351608087063850', '351608087064189', '351608087062852', '351608087075367', '351608087083940', '351608087083957', '351608087061888', '351608087061052', '351608087061987', '351608087060419', '351608087060765', '351608087062688', '351608087062787', '351608087060328', '351608087062357', '351608087062183', '351608087062670', '351608087060401', '351608087084757', '351608087084799', '351608087084419', '351608087084401', '351608087084427', '351608087079971', '351608087079963', '351608087079955', '351608087079948', '351608087079997']
                },

            }
        },
        {
            "$group" :{_id: "$devId","time": {$first: "$time"}, "lng": {$first: "$bLongitude"},"lat": {$first: "$bLatitude"},"model": {$first: "$model"},"speed": {$first: "$speed"}}
        },
        {
            "$project" :
             {
                "bLongitude" : "$lng",
                 "bLatitude" : "$lat",
                 "model" : "$model",
                 "speed" : "$speed",
                 "time" : "$time",     
            }
        },
         { "$sort" : { time : -1 }}
    ]
);

'''
# data = [{"imei": "351608087084708"}, {"imei": "351608087065392"}, {"imei": "351608087064395"},
#         {"imei": "351608087065434"}, {"imei": "351608087065053"}, {"imei": "351608087064338"},
#         {"imei": "351608087085846"}, {"imei": "351608087065046"}, {"imei": "351608087065400"},
#         {"imei": "351608087065111"}, {"imei": "351608087071911"}, {"imei": "351608087086018"},
#         {"imei": "351608087064312"}, {"imei": "351608087058751"}, {"imei": "351608087065418"},
#         {"imei": "351608087084732"}, {"imei": "351608087084443"}, {"imei": "351608087084468"},
#         {"imei": "351608087084484"}, {"imei": "351608087084450"}, {"imei": "351608087084435"},
#         {"imei": "351608087084781"}, {"imei": "351608087085994"}, {"imei": "351608087060120"},
#         {"imei": "351608087085929"}, {"imei": "351608087062373"}, {"imei": "351608087085903"},
#         {"imei": "351608087061318"}, {"imei": "351608087086091"}, {"imei": "351608087070020"},
#         {"imei": "351608087085978"}, {"imei": "351608087065558"}, {"imei": "351608087065731"},
#         {"imei": "351608087065582"}, {"imei": "351608087065533"}, {"imei": "351608087065749"},
#         {"imei": "351608087065574"}, {"imei": "351608087070210"}, {"imei": "351608087070194"},
#         {"imei": "351608087064973"}, {"imei": "351608087085879"}, {"imei": "351608087070327"},
#         {"imei": "351608087086059"}, {"imei": "351608087060906"}, {"imei": "351608087086067"},
#         {"imei": "351608087059171"}, {"imei": "351608086050825"}, {"imei": "351608087065095"},
#         {"imei": "351608087061508"}, {"imei": "351608086051153"}, {"imei": "351608087086083"},
#         {"imei": "351608087085911"}, {"imei": "351608087068131"}, {"imei": "351608087085895"},
#         {"imei": "351608087060682"}, {"imei": "351608087059320"}, {"imei": "351608087077694"},
#         {"imei": "351608087062589"}, {"imei": "351608087062399"}, {"imei": "351608087061284"},
#         {"imei": "351608087085986"}, {"imei": "351608087073453"}, {"imei": "351608087061730"},
#         {"imei": "351608087076498"}, {"imei": "351608087059023"}, {"imei": "351608087084740"},
#         {"imei": "351608086050734"}, {"imei": "351608086050510"}, {"imei": "351608086050809"},
#         {"imei": "351608086050940"}, {"imei": "351608086051161"}, {"imei": "351608086051120"},
#         {"imei": "351608086051187"}, {"imei": "351608086050882"}, {"imei": "351608086050551"},
#         {"imei": "351608086050866"}, {"imei": "351608086050569"}, {"imei": "351608086050593"},
#         {"imei": "351608086050767"}, {"imei": "351608086050452"}, {"imei": "351608086051005"},
#         {"imei": "351608086050775"}, {"imei": "351608086051179"}, {"imei": "351608086050536"},
#         {"imei": "351608086050874"}, {"imei": "351608086050411"}, {"imei": "351608086050577"},
#         {"imei": "351608086051021"}, {"imei": "351608086051013"}, {"imei": "351608086050858"},
#         {"imei": "351608086051195"}, {"imei": "351608086051203"}, {"imei": "351608087058199"},
#         {"imei": "351608087058215"}, {"imei": "351608087070640"}, {"imei": "351608087080359"},
#         {"imei": "351608087080326"}, {"imei": "351608087059940"}, {"imei": "351608087084773"},
#         {"imei": "351608087064908"}, {"imei": "351608087063850"}, {"imei": "351608087064189"},
#         {"imei": "351608087062852"}, {"imei": "351608087075367"}, {"imei": "351608087083940"},
#         {"imei": "351608087083957"}, {"imei": "351608087061888"}, {"imei": "351608087061052"},
#         {"imei": "351608087061987"}, {"imei": "351608087060419"}, {"imei": "351608087060765"},
#         {"imei": "351608087062688"}, {"imei": "351608087062787"}, {"imei": "351608087060328"},
#         {"imei": "351608087062357"}, {"imei": "351608087062183"}, {"imei": "351608087062670"},
#         {"imei": "351608087060401"}, {"imei": "351608087084757"}, {"imei": "351608087084799"},
#         {"imei": "351608087084419"}, {"imei": "351608087084401"}, {"imei": "351608087084427"},
#         {"imei": "351608087079971"}, {"imei": "351608087079963"}, {"imei": "351608087079955"},
#         {"imei": "351608087079948"}, {"imei": "351608087079997"}]
# for i in data:
#
# data2= [{"imei":"351608086035339"},{"imei":"351608086033805"},{"imei":"351608086035230"},{"imei":"351608086033516"},{"imei":"351608086033565"},{"imei":"351608086033912"},{"imei":"351608086034027"},{"imei":"351608086034423"},{"imei":"351608086033581"},{"imei":"351608086033789"},{"imei":"351608086021610"},{"imei":"351608086021768"},{"imei":"351608086021826"},{"imei":"351608086021545"},{"imei":"351608086021446"},{"imei":"351608086021453"},{"imei":"351608086021594"},{"imei":"351608086021214"},{"imei":"351608086020968"},{"imei":"351608086021438"}]
# a,b = distinguish_devices_type(data2)
# print(a)
# print(b)
# type2 = ['351608087065095', '351608087065418', '351608087058751', '351608087064312',
#          '351608087086018', '351608087071911', '351608087065111', '351608087065400', '351608087065046',
#          '351608087085846']
# type3 = ['351608086035339', '351608086033805', '351608086035230', '351608086033516', '351608086033565',
#          '351608086033912', '351608086034027', '351608086034423', '351608086033581', '351608086033789',
#          '351608086021610', '351608086021768', '351608086021826', '351608086021545', '351608086021446',
#          '351608086021453', '351608086021594', '351608086021214', '351608086020968', '351608086021438']
# type2=[]
# type3=['351608086033789', '351608086033581', '351608086034423', '351608086034027', '351608086033912', '351608086033565', '351608086033516', '351608086035230', '351608086033805', '351608086035339', '351608086043325', '351608086043853', '351608086043770', '351608086043309', '351608086043341', '351608086043572', '351608086043762', '351608086042996', '351608086043507', '351608086041055']
# #
# def test1(type2, type3):
#     a = get_type3_info(type3)
#     b = get_type2_info(type2)


# t1 = datetime.datetime.now()
# test1(type2, type3)
# t2 = datetime.datetime.now()
# print(t2 - t1)

# loop = asyncio.get_event_loop()
# tasks = [, ]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()


# def get_devices_info(type2, type3):
#     tasks = [
#         asyncio.ensure_future(get_type3_info(type3)),
#         asyncio.ensure_future(get_type2_info(type2))
#     ]
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(asyncio.wait(tasks))
#     l = []
#     for task in tasks:
#         l = l + task.result()
#     return l
#
#
# a = get_devices_info(type2, type3)
# print(a)
# dat = ['351608086044851', '351608086050098', '351608086048217', '351608086046260', '351608086049173', '351608086049512', '351608086021511', '351608086051104', '351608086050999', '351608086051070']
# a= get_type3_info(dat)
# print(a)
# data = {"Index_PactCode":"220545","Company_name":"湖北丰源物流供应链管理有限公司","Index_Code":"20042100827"}
# a = get_msg_info(CustomerSymbolName='惠洋电机',Company_name='湖北丰源物流供应链管理有限公司',Index_PactCode='220545')
# print(a)
