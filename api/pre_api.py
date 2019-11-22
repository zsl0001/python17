from flask import Flask
from flask import jsonify
from api_preceipt.my_db.my_sql import open_mysql
from api_preceipt.my_db.my_mgdb import my_mog
from flask_cors import  *
from flask import request
from bson import json_util
from werkzeug.datastructures import CombinedMultiDict, MultiDict
import json
#
my_mog = my_mog()
app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/Get_Sales_Name/',methods=['GET'])
def Get_Sales_Name():
    my=open_mysql()
    a = my.get_sales_name()
    a = jsonify(a)
    my.closeDb()
    return a

@app.route('/Get_Company_Name/',methods=['POST'])
def Get_Company_Name():
    my=open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        sales_name = data[0]['sales_name']
        # print(data)
    a = my.find_Company_name_by_sales_name(sales_name)
    a = jsonify(a)
    my.closeDb()
    return a

@app.route('/Get_Company_Device/',methods=['POST'])
def Get_Company_Device():
    my=open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        Company_Id = data[0]['Company_Id']
    a = my.find_Device_list_by_Company_Id(Company_Id)
    a = jsonify(a)
    my.closeDb()
    return a

@app.route('/Get_Device_Count/',methods=['GET'])
def Get_Company_Device_Count():
    my=open_mysql()
    size = request.args.get("size")
    page = request.args.get("page")
    a = my.Device_Count(page,size)
    a = jsonify(a)
    my.closeDb()
    return a

@app.route('/Get_Count_and_List/',methods=['GET'])
def Get_Count_and_List():
    my=open_mysql()
    a = my.find_count_and_List()
    a = jsonify(a)
    my.closeDb()
    return a

@app.route('/Get_Sales_List/',methods=['GET'])
def Get_Sales_List():
    my=open_mysql()
    a = my.Sales_device2()
    a = jsonify(a)
    my.closeDb()
    return a

@app.route('/Get_Device_list/',methods=['GET'])
def Get_Company_Device_list():
    my_sql = open_mysql()
    size = request.args.get("size")
    page = request.args.get("page")
    Device_CompanyID = request.args.get("Device_CompanyID")
    a = my_sql.Comp_Device(page,size,Device_CompanyID)
    a = jsonify(a)
    my_sql.closeDb()
    return a

@app.route('/Get_last_postion/',methods=['POST'])
def Get_last_postion(imei = None):
    my_sql = open_mysql()
    if request.method == 'POST':
        imei= request.get_json(force=True)
        print(imei)
        l = []
        if isinstance(imei,list):
            for i in imei:

                a = my_mog.find_last_postion(i['imei'])
                b = json_util.dumps(a)
                l.append(b)
                c =jsonify(l)
        else:
            a = my_mog.find_last_postion(imei)
            b = json_util.dumps(a)
            l.append(b)
            c = jsonify(l)
        my_sql.closeDb()
        return c

@app.route('/Get_status/<imei>/',methods=['GET','POST'])
def Get_status(imei = None):
    my_sql = open_mysql()
    a = my_mog.find_status(imei)
    a = jsonify(a)
    my_sql.closeDb()
    return a

@app.route('/Get_more_postion/',methods=['POST'])
def Get_more_postion(imei = None,start_time = None,end_Time=None):
    my_sql = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        # print(data)
        a = my_mog.find_more_postion(data[0]['imei'],data[1]['start_time'],data[2]['end_Time'])
        a = jsonify(a)
        print(a)
        my_sql.closeDb()
    return a

@app.route('/Get_Device_slepp_list/<imei>/<start_time>/<end_Time>/',methods=['GET','POST'])
def Get_Device_slepp_list(imei = None,start_time = None,end_Time=None):
    my_sql = open_mysql()
    a = my_mog.find_sleep(imei,start_time,end_Time)
    a = jsonify(a)
    my_sql.closeDb()
    return a

@app.route('/find_device_to_company_name/',methods=['POST'])
def Get_device_to_company_name():
    my_sql = open_mysql()
    if request.method == 'POST':
        l = []
        Company_Name = request.get_json(force=True)
        if isinstance(Company_Name,list):
            for name in Company_Name:
                a = my_sql.find_device_to_company_name(name["name"])
                l.append(a)
                c =jsonify(l)
                my_sql.closeDb()
        else:
            a = my_sql.find_device_to_company_name(Company_Name)
            l.append(a)
            c = jsonify(l)
            my_sql.closeDb()
        return c

@app.route('/find_device_to_imei/',methods=['POST'])
def Get_device_to_imei():
    my_sql = open_mysql()
    if request.method == 'POST':
        l = []
        imei = request.get_json(force=True)
        print(imei)
        if isinstance(imei,list):
            for name in imei:
                print(name["imei"])
                a = my_sql.find_device_to_imei(name["imei"])
                l.append(a)
                c =jsonify(l)
                my_sql.closeDb()
        else:
            a = my_sql.find_device_to_imei(imei)
            l.append(a)
            c = jsonify(l)
            my_sql.closeDb()
        return c


@app.route('/search_info/',methods=['POST'])
def Get_search_info():
    my_sql = open_mysql()
    if request.method == 'POST':
        l = []
        data = request.get_json(force=True)
        print(data)
        if len(str(data[1]['name'])) > 1 and len(str(data[0]['imei'])) > 1:
            return '不支持的查询方式'
        elif len(str(data[0]['imei'])) > 1:
             imei = data[0]['imei']
             if isinstance(imei,list):
                for name in imei:
                    a = my_sql.find_device_to_imei(name["imei"])
                    l.append(a)
                    c =jsonify(l)
                    my_sql.closeDb()
                    return c
             else:
                    a = my_sql.find_device_to_imei(imei)
                    l.append(a)
                    c = jsonify(l)
                    my_sql.closeDb()
                    return c
        elif len(str(data[1]['name'])) > 1:
            cp_name = data[1]['name']
            if isinstance(cp_name, list):
                for name in cp_name:
                    print(name["name"])
                    a = my_sql.find_device_to_company_name2(name["name"])
                    l.append(a)
                    c = jsonify(l)
                    my_sql.closeDb()
                    return c
            else:
                a = my_sql.find_device_to_company_name2(cp_name)
                l.append(a)
                c = jsonify(l)
                my_sql.closeDb()
                return c

@app.route('/get_msg/',methods=['POST'])
def Get_msg():
    my_sql = open_mysql()
    if request.method == 'POST':
        l = []
        data = request.get_json(force=True)
        print(data)
        Company_Name = data[0]['Company_Name']
        Index_PactCode = data[1]["Index_PactCode"]
        a = my_mog.find_msg_by_imei(Company_Name,Index_PactCode)
        l = jsonify(a)
        my_sql.closeDb()
        return l

@app.route('/get_pactcode/',methods=['POST'])
def Get_Pactcode():
    my_sql = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)
        imei = data[0]["imei"]
        page = data[1]["page"]
        size = data[2]["size"]
        a = my_sql.fint_pactcode_by_imei(imei,page,size)
        c = jsonify(a)
        my_sql.closeDb()
        return c



if __name__ == '__main__':
    app.run(host='0.0.0.0',  # 设置ip，默认127.0.0.1
            port=7777,  # 设置端口，默认5000
            debug=None)  # 设置是否开启调试，默认false