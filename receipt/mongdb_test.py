import pymongo
import faker
import datetime
f = faker.Faker(locale='zh-CN')
myclient = pymongo.MongoClient("mongodb://192.168.1.45:27017/")
mydb = myclient["er"]

longitude = 116.414789
latitude = 39.91146
imei = 351608087500000
count = 0
while count < 10:
    last_end = str(imei)[-1]
    count = count + 1
    col = 'position'+last_end
    print(col)
    longitude = longitude + 0.00001
    latitude = latitude + 0.00001
    mycol = mydb[col]
    my_data = {
        "devId": str(imei),
        # "_class": "com.yellows.mongo.dao.model."+ col,
        "longitude": longitude,
        "latitude": latitude,
        "bLongitude": longitude,
        "bLatitude": latitude,
        "model": 0,
        "type": 0,
        "mcc": 2,
        "mnc": 0,
        "lac": 0,
        "cellId": 0,
        "time": datetime.datetime.now(),
        "course": 122,
        "speed": 122.0
    }
    print(my_data)
    x = mycol.insert_one(my_data)
    print(x)
    imei = imei + 1