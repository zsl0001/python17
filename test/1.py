import pymongo

client = pymongo.MongoClient(
    'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
# 连接所需数据库,er为数据库名
db = client.er
log = db.log
# /home/nanruan/test
with open(r'/home/nanruan/test/06112.txt', 'r') as f:
    d = f.readlines()
    for i in d:
        sql = {'imei': str(i.strip('\n'))}
        l = []
        result = log.find(sql).sort("time", -1).limit(1)
        for d in result:
            mode = d['content'].split(',')[0]
            mode2 = d['content'].split(',')[1]
            if int(mode2) <= 100:
                with open(r'/home/nanruan/test/mode1.txt', 'a+') as f:
                    f.write(i)
            else:
                with open(r'/home/nanruan/test/mode2.txt', 'a+') as f:
                    f.write(i)
