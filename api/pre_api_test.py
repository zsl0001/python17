from api_preceipt.models import app, db, User, TMSSale
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bson import json_util
from api_preceipt import models
from api_preceipt.my_db import Models
from flask import request
from flask import jsonify, Blueprint
from sqlalchemy import and_
from api_preceipt.my_db.my_sql import open_mysql
from api_preceipt.my_db.my_mgdb import my_mog
from api_preceipt.my_db.my_models import My_Models
from flask import Flask, abort, request, jsonify, g, url_for, make_response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import base64
from flask_cors import *
from flask_docs import ApiDoc
from api_preceipt.api.login_mode.response_code import RET

executor = ThreadPoolExecutor(2)
my = open_mysql()
ApiDoc(app)
#
auth = HTTPBasicAuth()
app.config['API_DOC_MEMBER'] = ['api']

api = Blueprint('app', __name__)


def get_basic_auth_str(username, password=''):
    temp_str = username + ':' + password
    # 转成bytes string
    bytesString = temp_str.encode(encoding="utf-8")
    # base64 编码
    encodestr = base64.b64encode(bytesString)
    # 解码
    decodestr = base64.b64decode(encodestr)

    return 'Basic ' + encodestr.decode()


@api.route('/signin', methods=['POST'])
@auth.login_required
def signin():
    '''用户注册接口
    :return 返回注册信息{'re_code': '0', 'msg': '注册成功'}
    '''
    Sales_Set_Log = models.SalesSetLog()
    ip = request.remote_addr
    data = request.get_json(force=True)
    username = request.json.get('username')
    password = request.json.get('password')
    sales_name = request.json.get('sales_name')
    role_id = request.json.get('role_id')

    if not all([username, password, sales_name, role_id]):
        return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
    user = User()
    if role_id != 1:
        return jsonify(re_code=RET.DBERR, msg='权限不足')
    else:
        if User.query.filter(and_(User.username == username, User.is_disable != 1)).first() != None:
            return jsonify(re_code=RET.DBERR, msg='账号已经存在')
        user.username = username
        user.password = password
        user.sales_name = sales_name  # 利用user model中的类属性方法加密用户的密码并存入数据库
        Sales_Set_Log.Creator_Name = User.query.filter(User.role_id == 1).first().username
        Sales_Set_Log.Insert_Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Sales_Set_Log.IP = ip
        Sales_Set_Log.User_Name = username
        Sales_Set_Log.Content = '{}在{}，新增了用户{}，所在地IP地址为:{}。'.format(Sales_Set_Log.Creator_Name,
                                                                    Sales_Set_Log.Insert_Time, user.sales_name,
                                                                    Sales_Set_Log.IP)
    try:
        db.session.add(user)
        db.session.add(Sales_Set_Log)
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='注册失败')
    # 6.响应结果
    return jsonify(re_code=RET.OK, msg='注册成功')


@api.route('/login', methods=['POST'])
def login():
    '''登录
    TODO: 添加图片验证
    :return 返回响应,保持登录状态
    '''
    data = request.get_json(force=True)
    username = data['username']
    password = data['password']

    # 解析Authorization
    # email, password = base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode().split(':')

    if not all([username, password]):
        return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
    try:
        user = User.query.filter(User.username == username, User.is_disable == 0).first()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(re_code=RET.DBERR, msg='查询用户失败')
    if not user:
        return jsonify(re_code=RET.NODATA, msg='用户不存在', user=user)
    if not user.verify_password(password):
        return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
    # 更新最后一次登录时间
    user.update_last_seen()
    token = user.generate_user_token()
    token = get_basic_auth_str(token)
    return jsonify(re_code=RET.OK, msg='登录成功', token=token, sales_name=user.sales_name, id=user.id,
                   role_id=user.role_id)


@auth.verify_password
def verify_password(username_or_token, password):
    if request.path == '/login':
        user = User.query.filter_by(email=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.verify_user_token(username_or_token)
        if not user:
            return False
    g.user = user
    return True


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 201)


@api.route('/Get_List/', methods=['POST'])
def Get_List():
    my = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        sales_company = data[0]['sales_company']
    a = my.find_Company_name_and_Device_list(sales_company)
    a = jsonify(a)
    my.closeDb()
    return a


@api.route('/')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@api.route('/Get_Sales_Name/', methods=['GET'])
def Get_Sales_Name():
    my = open_mysql()
    a = my.get_sales_name()
    a = jsonify(a)
    my.closeDb()
    return a


@api.route('/Get_Company_Name/', methods=['POST'])
def Get_Company_Name():
    my = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        sales_name = data[0]['sales_name']
        # print(data)
    a = my.find_Company_name_by_sales_name(sales_name)
    a = jsonify(a)
    my.closeDb()
    return a


@api.route('/Get_Company_Device/', methods=['POST'])
def Get_Company_Device():
    my = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        Company_Id = data[0]['Company_Id']
    a = my.find_Device_list_by_Company_Id(Company_Id)
    a = jsonify(a)
    my.closeDb()
    return a


@api.route('/Get_Device_Count/', methods=['GET'])
def Get_Company_Device_Count():
    my = open_mysql()
    size = request.args.get("size")
    page = request.args.get("page")
    a = my.Device_Count(page, size)
    a = jsonify(a)
    my.closeDb()
    return a


@api.route('/Get_Count_and_List/', methods=['GET'])
def Get_Count_and_List():
    my = open_mysql()
    a = my.find_count_and_List()
    a = jsonify(a)
    my.closeDb()
    return a


@api.route('/Get_Sales_List/', methods=['GET'])
def Get_Sales_List():
    my = open_mysql()
    a = my.Sales_device2()
    a = jsonify(a)
    my.closeDb()
    return a


@api.route('/Get_Device_list/', methods=['GET'])
def Get_Company_Device_list():
    my_sql = open_mysql()
    size = request.args.get("size")
    page = request.args.get("page")
    Device_CompanyID = request.args.get("Device_CompanyID")
    a = my_sql.Comp_Device(page, size, Device_CompanyID)
    a = jsonify(a)
    my_sql.closeDb()
    return a


def get_devices_info(type2, type3):
    tasks = [
        asyncio.ensure_future(Models.get_type3_info(type3)),
        asyncio.ensure_future(Models.get_type2_info(type2))
    ]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    l = []
    for task in tasks:
        l = l + task.result()
    return l


@api.route('/get_last_position/', methods=['POST'])
@auth.login_required
def Get_last_postion(imei=None):
    my_sql = open_mysql()
    if request.method == 'POST':
        imei = request.get_json(force=True)
        a = Models.get_last_position(imei)
        c = jsonify(a)
        return c


@api.route('/get_devices_info/', methods=['POST'])
@auth.login_required
def devices_info(imei=None):
    my_sql = open_mysql()
    if request.method == 'POST':
        imei = request.get_json(force=True)
        # a = Models.get_devices_info(imei)
        # c =jsonify(a)
        type2, type3 = Models.distinguish_devices_type(imei)
        a = Models.get_devices_info3(type2=type2, type3=type3)
        c = jsonify(a)
        return c


@api.route('/Get_status/<imei>/', methods=['GET', 'POST'])
def Get_status(imei=None):
    my_sql = open_mysql()
    a = my_mog.find_status(imei)
    a = jsonify(a)
    my_sql.closeDb()
    return a


@api.route('/Get_more_postion/', methods=['POST'])
def Get_more_postion(imei=None, start_time=None, end_Time=None):
    my_sql = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        a = my_mog.find_more_postion(data[0]['imei'], data[1]['start_time'], data[2]['end_Time'])
        a = jsonify(a)
        my_sql.closeDb()
    return a


@api.route('/Get_Device_slepp_list/<imei>/<start_time>/<end_Time>/', methods=['GET', 'POST'])
def Get_Device_slepp_list(imei=None, start_time=None, end_Time=None):
    my_sql = open_mysql()
    a = my_mog.find_sleep(imei, start_time, end_Time)
    a = jsonify(a)
    my_sql.closeDb()
    return a


@api.route('/find_device_to_company_name/', methods=['POST'])
def Get_device_to_company_name():
    my_sql = open_mysql()
    if request.method == 'POST':
        l = []
        Company_Name = request.get_json(force=True)
        if isinstance(Company_Name, list):
            for name in Company_Name:
                a = my_sql.find_device_to_company_name(name["name"])
                l.append(a)
                c = jsonify(l)
                my_sql.closeDb()
        else:
            a = my_sql.find_device_to_company_name(Company_Name)
            l.append(a)
            c = jsonify(l)
            my_sql.closeDb()
        return c


@api.route('/find_device_to_imei/', methods=['POST'])
def Get_device_to_imei():
    my_sql = open_mysql()
    if request.method == 'POST':
        l = []
        imei = request.get_json(force=True)
        if isinstance(imei, list):
            for name in imei:
                a = my_sql.find_device_to_imei(name["imei"])
                l.append(a)
                c = jsonify(l)
                my_sql.closeDb()
        else:
            a = my_sql.find_device_to_imei(imei)
            l.append(a)
            c = jsonify(l)
            my_sql.closeDb()
        return c


@api.route('/search_info/', methods=['POST'])
def Get_search_info():
    my_sql = open_mysql()
    if request.method == 'POST':
        l = []
        data = request.get_json(force=True)
        if len(str(data[1]['name'])) > 1 and len(str(data[0]['imei'])) > 1:
            return '不支持的查询方式'
        elif len(str(data[0]['imei'])) > 1:
            imei = data[0]['imei']
            if isinstance(imei, list):
                for name in imei:
                    a = my_sql.find_device_to_imei(name["imei"])
                    l.append(a)
                    c = jsonify(l)
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


@api.route('/get_msg/', methods=['POST'])
@auth.login_required
def Get_msg():
    my_sql = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        Index_Code = request.json.get('Index_Code')
        Index_PactCode = request.json.get('Index_PactCode')
        Company_name = request.json.get('Company_name')
        if not all([Company_name, Index_Code, Index_PactCode]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        else:
            a = Models.get_msg_info(Company_name=Company_name, Index_PactCode=Index_PactCode, Index_Code=Index_Code)
            l = jsonify(a)
        return l


@api.route('/get_pactcode/', methods=['POST'])
@auth.login_required
def Get_Pactcode():
    my_sql = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        # imei = data["imei"]
        page = data["page"]
        size = data["size"]
        a = my_sql.fint_pactcode_by_imei(page, size)
        c = jsonify(a)
        my_sql.closeDb()
        return c


@api.route('/get_more_sleepNotice/', methods=['POST'])
@auth.login_required
def Get_More_SleepNotice():
    if request.method == 'POST':
        data = request.get_json(force=True)
        imei = data[0]["imei"]
        start_time = data[1]["start_time"]
        end_Time = data[2]["end_Time"]
        page = data[3]["page"]
        size = data[4]["size"]
        a = my_mog.find_more_sleepNotice(imei, start_time, end_Time, size, page)
        c = jsonify(a)
        return c


@api.route('/get_last_sleepNotice/', methods=['POST'])
@auth.login_required
def Get_Last_SleepNotice():
    if request.method == 'POST':
        data = request.get_json(force=True)
        imei = data[0]['imei']
        a = my_mog.find_last_sleepNotice(imei)
        c = jsonify(a)
        return c


@api.route('/get_Sales_and_Device_list/', methods=['POST'])
@auth.login_required
def Get_Sales_and_Device_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = data['page']
        size = data['size']
        my = open_mysql()
        a = my.find_Sales_and_Device_list(page=page, size=size)
        c = jsonify(a)
        my.closeDb()
        return c


@api.route('/get_device_list_by_sales_company/', methods=['POST'])
def Get_device_list_by_sales_company():
    if request.method == 'POST':
        data = request.get_json(force=True)
        sales_company = data['sales_company']
        my = open_mysql()
        a = my.find_device_list_by_sales_company(sales_company=sales_company)
        c = jsonify(a)
        my.closeDb()
        return c


@api.route('/get_info_by_imei/', methods=['POST'])
def Get_info_by_imei():
    if request.method == 'POST':
        data = request.get_json(force=True)
        IMEI = data['IMEI']
        a = models.find_imei_info(IMEI)
        c = jsonify(a)
        return c


@api.route('/get_all_imei/', methods=['POST'])
@auth.login_required
def Get_all_imei():
    if request.method == 'POST':
        data = request.get_json(force=True)
        a = models.get_all_imei(id=int(data['id']))
        c = jsonify(a)
        return c


@api.route('/search_imei_info/', methods=['POST'])
@auth.login_required
def Search_imei_info():
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = request.json.get('page')
        size = request.json.get('size')
        id = request.json.get('role_id')
        type = request.json.get('type')
        # if not all([page,size,id,type]):
        #     return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        a = models.search_imei_info2(data)
        c = jsonify(a)
        return c


@api.route('/get_expire_imei_list/', methods=['POST'])
@auth.login_required
def Get_expire_imei_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        tp = data['type']
        page = data['page']
        size = data['size']
        id = int(data['id'])
        a = models.get_expire_imei_list(tp=tp, page=page, size=size, id=id)
        c = jsonify(a)
        return c


@api.route('/get_alarm_list/', methods=['POST'])
@auth.login_required
def Get_alarm_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = data['page']
        size = data['size']
        a = My_Models()
        dd = models.get_company_id_and_name(page, size)
        d = a.get_3imei_info(page, size, data=dd)
        c = jsonify(d)
        return c


@api.route('/search_alarm_list/', methods=['POST'])
@auth.login_required
def search_alarm_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = data['page']
        size = data['size']
        id = int(data['id'])
        a = My_Models()
        dd, d2 = models.search_get_alarm_list(data, page, size, id)
        d3 = {
            "count": d2
        }
        d = a.get_3imei_info(page, size, data=dd)
        d = {**d, **d3}
        c = jsonify(d)
        return c


@api.route('/get_alarm_info/', methods=['POST'])
@auth.login_required
def Get_alarm_info():
    if request.method == 'POST':
        da = request.get_json(force=True)
        data = models.get_all_company_id_and_name(id=da['id'])
        a = My_Models()
        d = a.get_alarm2(data)
        c = jsonify(d)
        ip = request.remote_addr
        return c


@api.route('/search_alarm_info/', methods=['POST'])
@auth.login_required
def search_alarm_info():
    if request.method == 'POST':
        d = request.get_json(force=True)
        data = models.search_alarm_list(d)
        l = []
        l.append(data)
        a = My_Models()
        d = a.get_alarm(l)
        c = jsonify(d)
        ip = request.remote_addr
        return c


@api.route('/search_pactcode/', methods=['POST'])
@auth.login_required
def search_pactcode_by_imei():
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = data['page']
        size = data['size']
        id = int(data['id'])
        d = models.search_pactcode_by_imei(data, page, size, id)
        c = jsonify(d)
        return c


@api.route('/assignment_company', methods=['POST'])  # 给销售分配公司
@auth.login_required
def assignment_company():
    if request.method == 'POST':
        data = request.get_json(force=True)
        Company_ClientCode = request.json.get('Company_ClientCode')
        role_id = request.json.get('role_id')
        Sales_Company = request.json.get('Sales_Company')
        if not all([Company_ClientCode, role_id, Sales_Company]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        if role_id != 1:
            return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            res = models.assignment_company(data)
        return jsonify(res)


@api.route('/get_sales_list', methods=['POST'])  # 获取销售列表
@auth.login_required
def get_sales_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = request.json.get('page')
        size = request.json.get('size')
        role_id = request.json.get('role_id')
        if not all([page, size, role_id]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        if role_id != 1:
            return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            res = models.get_sales_list(page, size)
        return jsonify(res)


@api.route('/search_company_list', methods=['POST'])  # 搜索公司列表
@auth.login_required
def search_company_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = request.json.get('page')
        size = request.json.get('size')
        role_id = request.json.get('role_id')
        user_id = request.json.get('user_id')
        if not all([page, size, role_id, user_id]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        if role_id != 1:
            return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            res = models.search_company_list(user_id, page, size)
        return jsonify(res)


@api.route('/set_account_properties', methods=['POST'])  # 启用，禁用，修改账号密码
@auth.login_required
def set_account_properties():
    if request.method == 'POST':
        Sales_Set_Log = models.SalesSetLog()
        ip = request.remote_addr
        data = request.get_json(force=True)
        is_disable = request.json.get('is_disable')
        password = request.json.get('password')
        role_id = request.json.get('role_id')
        user_id = request.json.get('user_id')
        type = request.json.get('type')  # 1为改密码，2为启用禁用
        if not all([str(is_disable), str(password), role_id, user_id, type]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        if role_id != 1:
            return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            Sales_Set_Log.User_Name = User.query.filter(User.id == user_id).first().username
            res = models.set_account_properties(data)
            Sales_Set_Log.Creator_Name = User.query.filter(User.role_id == 1).first().username
            Sales_Set_Log.Insert_Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Sales_Set_Log.IP = ip
            if type == 1:
                Sales_Set_Log.Content = '{}在{},修改了用户{}的密码,操作地IP为{}。'.format(Sales_Set_Log.Creator_Name,
                                                                            Sales_Set_Log.Insert_Time,
                                                                            Sales_Set_Log.User_Name, ip)
                db.session.add(Sales_Set_Log)
                db.session.commit()
            if type == 2:
                if is_disable == 0:
                    Sales_Set_Log.Content = '{}在{},启用了用户{}，操作所在地IP为{}。'.format(Sales_Set_Log.Creator_Name,
                                                                               Sales_Set_Log.Insert_Time,
                                                                               Sales_Set_Log.User_Name, ip)
                    db.session.add(Sales_Set_Log)
                    db.session.commit()
                if is_disable == 1:
                    Sales_Set_Log.Content = '{}在{},禁用了用户{}，操作所在地IP为{}。'.format(Sales_Set_Log.Creator_Name,
                                                                               Sales_Set_Log.Insert_Time,
                                                                               Sales_Set_Log.User_Name, ip)
                    db.session.add(Sales_Set_Log)
                    db.session.commit()
        return jsonify(res)


@api.route('/search_sales_info', methods=['POST'])
@auth.login_required
def search_sales_info():
    if request.method == 'POST':
        data = request.get_json(force=True)
        Company_name = request.json.get('Company_Name')
        Sales_name = request.json.get('Sales_name')
        page = request.json.get('page')
        size = request.json.get('size')
        role_id = request.json.get('role_id')
        if role_id != 1:
            return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            res = models.get_sales_list2(data)
        return jsonify(res)


@api.route('/get_elc/', methods=['POST'])
@auth.login_required
def get_elc():  # 获取电量
    my_sql = open_mysql()
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['imei'][8] == '6':
            a = Models.get_elc_type3(data['imei'], start=data['startTime'], end=data['endTime'], page=data['page'],
                                     size=data['size'])
            c = jsonify(a)
        else:
            a = Models.get_elc_type2(data['imei'], start=data['startTime'], end=data['endTime'], page=data['page'],
                                     size=data['size'])
            c = jsonify(a)
        return c


@api.route('/change_sales_company/', methods=['POST'])
@auth.login_required
def change_sales_company():  #
    my_sql = open_mysql()
    ip = request.remote_addr
    Sales_Set_Log = models.SalesSetLog()
    if request.method == 'POST':
        data = request.get_json(force=True)  # Company_Id, user_id=None, disable=0,
        if 'user_name' in data.keys():
            a = models.change_sales_company(Company_Id=data['Company_Id'], user_name=data['user_name'],
                                            disable=data['disable'])
            Sales_Set_Log.User_Name = data['user_name']
            Sales_Set_Log.Creator_Name = User.query.filter(User.id == data['id']).first().username
            Sales_Set_Log.Insert_Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Sales_Set_Log.IP = ip
            Company_Name = TMSSale.query.filter(TMSSale.Company_Id == data['Company_Id']).first().Company_Name
            Sales_Set_Log.Company_ID = data['Company_Id']
            Sales_Set_Log.Content = '{}在{},将{}(公司名)所属销售变更为{},操作所在地IP为:{}。'.format(Sales_Set_Log.Creator_Name,
                                                                                  Sales_Set_Log.Insert_Time,
                                                                                  Company_Name, data['user_name'], ip)
        else:
            a = models.change_sales_company(Company_Id=data['Company_Id'], disable=data['disable'])
            user_id = TMSSale.query.filter(TMSSale.Company_Id == data['Company_Id']).first().user_id
            Sales_Set_Log.User_Name = User.query.filter(User.id == user_id).first().username
            Sales_Set_Log.Creator_Name = User.query.filter(User.id == data['id']).first().username
            Sales_Set_Log.Insert_Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Sales_Set_Log.IP = ip
            Company_Name = TMSSale.query.filter(TMSSale.Company_Id == data['Company_Id']).first().Company_Name
            Sales_Set_Log.Company_ID = data['Company_Id']
            Sales_Set_Log.Content = '{}在{},禁用了{}名下的{}(公司名),操作所在地IP为:{}。'.format(Sales_Set_Log.Creator_Name,
                                                                                Sales_Set_Log.Insert_Time,
                                                                                Sales_Set_Log.User_Name, Company_Name,
                                                                                ip)
        c = jsonify(a)
        db.session.add(Sales_Set_Log)
        db.session.commit()
        return c


@api.route('/get_sales_log/', methods=['POST'])
@auth.login_required
def get_sales_log():  # 获取电量
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = data['page']
        size = data['size']
        username = data['username']
        role_id = data['role_id']
        if not all([page, size, username, role_id]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        # if role_id !=1:
        #     return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            a = models.get_sales_log(username=data['username'], page=data['page'], size=data['size'])
            c = jsonify(a)
        return c


@api.route('/renew_device/', methods=['POST'])
@auth.login_required
def renew_device():  # 获取电量
    if request.method == 'POST':
        data = request.get_json(force=True)
        end_time = data['end_time']
        imei = data['imei']
        user_id = int(data['user_id'])
        if not all([user_id, imei, end_time]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        else:
            a = models.renew_device(user_id=data['user_id'], imei=data['imei'], end_time=data['end_time'],
                                    ip=request.remote_addr)
            c = jsonify(a)
        return c


@api.route('/get_msg_count/', methods=['POST'])
@auth.login_required
def get_msg_count():  # 获取电量
    if request.method == 'POST':
        data = request.get_json(force=True)
        end_time = data['end_time']
        user_id = int(data['user_id'])
        if not all([user_id, end_time]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        else:
            a = models.get_msg_count(user_id=data['user_id'], day_now=data['end_time'])
            c = jsonify(a)
        return c


app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0',  # 设置ip，默认127.0.0.1
            port=7777,  # 设置端口，默认5000
            debug=None,
            threaded=True)  # 设置是否开启调试，默认false
