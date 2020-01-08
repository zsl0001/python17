import mongoengine

con = mongoengine.connect('er', host='192.168.1.168', port=27017)


class Status(mongoengine.Document):
    meta = {
        'collection': 'status',
    }
    devId = mongoengine.StringField()
    date = mongoengine.DateTimeField()
    _class = mongoengine.StringField()
    lithium = mongoengine.IntField()
    gsmLevel = mongoengine.IntField()
    charging = mongoengine.IntField()


class ArriveMessage(mongoengine.Document):
    meta = {
        'collection': 'arriveMessage',
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
        'collection': 'devInfo',
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


class EndedMessage(mongoengine.Document):
    meta = {
        'collection': 'endedMessage',
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


class Position(mongoengine.Document):
    meta = {
        'collection': 'position',
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
        'collection': 'sleepNotice',
    }

    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    date = mongoengine.DateTimeField()
    res = mongoengine.BooleanField()
    tag = mongoengine.IntField()
    imei = mongoengine.StringField()


class SmsQueue(mongoengine.Document):
    meta = {
        'collection': 'smsQueue',
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
        'collection': 'arriveMestartMessagessage',
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
        'collection': 'status',
    }
    _id = mongoengine.StringField()
    _class = mongoengine.StringField()
    lithium = mongoengine.IntField()
    gsmLevel = mongoengine.IntField()
    charging = mongoengine.IntField()
    devId = mongoengine.StringField()
    date = mongoengine.DateTimeField()


data = Position.objects().filter(mongoengine.Q(time__gte='2019-06-13 00:00:00') & mongoengine.Q(time__lte='2019-06-15 00:00:00'))
# print(data.bLongitude)
# for i in data:
#     print(i.bLongitude)
print(len(data))
