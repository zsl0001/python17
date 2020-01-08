from flask import Flask
from flask import jsonify
import pymongo
import time
app = Flask(__name__)

@app.route('/Get_orderResult/<imei>/<token>/',methods=['GET','POST'])
def db_orderResult(imei,token):
    if token =='post123':
        client = pymongo.MongoClient(
            'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
        # 连接所需数据库,er为数据库名
        db = client.er
        collection = db.orderResult
        sql = {'devId': imei}
        # print(sql)
        result = collection.find(sql).sort("date", -1).limit(1)
        l = []
        data = {
            'tag':'',
            'devId':'',
            'res':''
        }
        for i in result:
            # print(i)
            data['tag'] = i['tag']
            data['devId'] = i['devId']
            data['res'] = i['res']
            # l.append(data.copy())
        res = jsonify(data)
        client.close()
        return res
    else:
        return '大清亡了'

@app.route('/Get_status/<imei>/<token>/',methods=['GET','POST'])
def db_status(imei,token):
    if token =='post123':
        client = pymongo.MongoClient(
            'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
        # 连接所需数据库,er为数据库名
        db = client.er
        collection = db.status
        sql = {'devId': imei}
        # print(sql)
        result = collection.find(sql).sort("date", -1).limit(1)
        l = []
        data = {
            'charging':'',
            'devId':'',
            'lithium':'',
        }
        for i in result:
            print(i)
            data['charging'] = i['charging']
            data['devId'] = i['devId']
            data['lithium'] = i['lithium']
            # l.append(data.copy())
        res = jsonify(data)
        client.close()
        return res
    else:
        return '大清亡了'

@app.route('/Get_devInfo/<imei>/<token>/',methods=['GET','POST'])
def db_devInfo(imei,token):
    if token =='post123':
        client = pymongo.MongoClient(
            'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
        # 连接所需数据库,er为数据库名
        db = client.er
        collection = db.devInfo
        sql = {'devId': imei}
        # print(sql)
        result = collection.find(sql).sort("status.date", -1).limit(1)
        l = []
        data = {
            'posInvl':'',
            'devId':'',
            'hbInvl':'',
        }
        for i in result:
            print(i)
            data['posInvl'] = i['posInvl']
            data['devId'] = i['devId']
            data['hbInvl'] = i['hbInvl']
            # l.append(data.copy())
        res = jsonify(data)
        client.close()
        return res
    else:
        return '大清亡了'

@app.route('/Get_elc/<imei>/<token>/',methods=['GET','POST'])
def db_electric(imei,token):
    if token == 'post123':
        client = pymongo.MongoClient(
            'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
        # 连接所需数据库,er为数据库名
        db = client.er
        collection = db.log
        sql = {'imei': imei}
        # print(sql)
        result = collection.find(sql).sort("time", -1).limit(1)
        l = []
        data = {
            'imei': '',
            'content': '',
            'time':''
        }
        for i in result:
            print(i)
            data['imei'] = i['imei']
            data['content'] = i['content']
            data['time'] = i['time'].strftime("%Y-%m-%d %H:%M:%S")
            # l.append(data.copy())
        res = jsonify(data)
        return res
    else:
        return '大清亡了'

@app.route('/Get_order/<imei>/<tag>/<token>/',methods=['GET','POST'])
def Get_order(imei,tag,token):
    if token == 'post123':
        client = pymongo.MongoClient(
            'mongodb://er_user:vE0UmSo1fV3q@dds-uf6a4f0597f9e3041.mongodb.rds.aliyuncs.com:3717,dds-uf6a4f0597f9e3042.mongodb.rds.aliyuncs.com:3717/er?replicaSet=mgset-13011481')
        # 连接所需数据库,er为数据库名
        db = client.er
        collection = db.orderResult
        sql = {'devId':imei,'tag':eval(tag)}
        print(sql)
        result = collection.find(sql).sort("date", -1).count()
        print(result)
        if result > 0:
            return "修改成功"
        else:
            return "修改失败"
    else:
        return '大清亡了'

if __name__ == '__main__':
    app.run(host='0.0.0.0',  # 设置ip，默认127.0.0.1
            port=8077,  # 设置端口，默认5000
            debug=None)  # 设置是否开启调试，默认false