# from api_preceipt.models import app,db, User, TMSSale,CPUser
from flask_apscheduler import APScheduler
import asyncio
import os
from flask import send_from_directory
from flask import url_for
import flask_excel as excel
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bson import json_util
# from api_preceipt import models
# from api_preceipt.my_db import Models
from flask import request,session
from flask import jsonify, Blueprint
from sqlalchemy import and_
# from api_preceipt.my_db.my_sql import open_mysql
# from api_preceipt.my_db.my_mgdb import my_mog
# from api_preceipt.my_db.my_models import My_Models
from flask import Flask, abort, request, jsonify, g, url_for, make_response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import base64
from flask_cors import *
from flask_docs import ApiDoc
# from api_preceipt.api.login_mode.response_code import RET
# from api_preceipt.api.set_name import Set_Name
# from api_preceipt.api.sales_tree import sales_tree
# from api_preceipt.api.edit_department import Edit_deppart
# from api_preceipt.api.get_sales_company_info import sales_company
# from api_preceipt.api.search_sales_tree import Search_sales_tree
# from api_preceipt.api.get_more_postion import  More_Position
# from api_preceipt.api.device_stock import  device_stock
# from api_preceipt.api.login_mode.validatecode import VercCode
# from api_preceipt.api.login_mode.pic.cutimg import getAuthImage,AuthImage,get_redis_res
from resources_files import *

# change_sales_company

executor = ThreadPoolExecutor(5)
my = open_mysql()
ApiDoc(app)
#
auth = HTTPBasicAuth()
app.config['API_DOC_MEMBER'] = ['api']

api = Blueprint('app', __name__)
class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        # {  # 第一个任务
        #     'id': 'job1',
        #     'func': '__main__:job_1',
        #     'args': (1, 2),
        #     'trigger': 'cron', # cron表示定时任务
        #     'hour': 19,
        #     'minute': 27
        # },
        {  # 第二个任务，每隔5S执行一次
            'id': 'job2',
            'func': '__main__:aotu_send_cmd', # 方法名
            'args': ({"type": "7", "User_name": "kf02", "user_id": "84", "page": 1, "size": 10, "id": "84", "username": "客服2", "useraccount": "kf02"},'192.168.1.1'), # 入参
            'trigger': 'interval', # interval表示循环任务
            'seconds':300,
        }]

def aotu_send_cmd(a,b):
    set_name = Set_Name(data=a,ip=b)
    set_name.aotu_send_cmd()
    print('发送成功')

app.config.from_object(Config())

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
    入参：
         username 注册账号
         password 初始密码
         sales_name 注册销售姓名
         role_id 角色ID，只有role_id 为1的才能创建账号。
    数据格式：
        {
        'username':'',
        'password':'',
        'sales_name':'',
        'role_id':''
        }
    出参：
        返回注册信息{'re_code': '0', 'msg': '注册成功'}
    '''
    Sales_Set_Log = models.SalesSetLog()
    ip = request.headers['X-Real-Ip']
    data = request.get_json(force=True)
    username = request.json.get('username')
    password = request.json.get('password')
    sales_name = request.json.get('sales_name')
    salesaccount = request.json.get('salesaccount')
    role_id = request.json.get('role_id')
    parent_id = request.json.get('parent_id')
    top_parent_id = request.json.get('top_parent_id')
    is_manager = request.json.get('is_manager')
    if not all([username, password, sales_name, role_id]):
        return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
    user = User()
    if role_id != 1:
        return jsonify(re_code=RET.DBERR, msg='权限不足')
    else:
        if User.query.filter(and_(User.username == salesaccount, User.is_disable != 1)).first() != None:
            return jsonify(re_code=RET.DBERR, msg='账号已经存在')
        user.username = salesaccount
        user.password = password
        user.is_manager = is_manager
        user.top_parent_id = top_parent_id
        user.parent_id = parent_id
        user.sales_name = sales_name  # 利用user model中的类属性方法加密用户的密码并存入数据库
        Sales_Set_Log.Creator_Name = User.query.filter(User.role_id == 1).first().username
        Sales_Set_Log.Insert_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Sales_Set_Log.IP = ip
        Sales_Set_Log.User_Name = salesaccount
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
    入参：
        username 用户名
        password 密码
    数据格式：
        {
        'username':'',
        'password':''
        }
    出参：
        返回值(msg='登录成功', token, sales_name(销售名字),id(用户唯一ID),role_id(用户角色ID，1为超级管理员，0位普通用户))
    '''

    data = request.get_json(force=True)
    username = data['username']
    password = data['password']
    uid = data['uid']
    # 解析Authorization
    # email, password = base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode().split(':')
    res = get_redis_res(uid=uid)
    if res =='True':
        if not all([username, password]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        try:
            user = User.query.filter(User.username == username, User.is_disable == 0).first()
            cp_user = CPUser.query.filter(CPUser.CP_UserCode == username, CPUser.CP_Enable == 1).first()
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(re_code=RET.DBERR, msg='查询用户失败')
        if not user and not cp_user:
            return jsonify(re_code=RET.NODATA, msg='用户不存在', user=user)
        if user == None:
            if  cp_user.verify_password(password) is not True:
                return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
        if cp_user == None:
            if  user.verify_password(password) is not True:
                return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
        # if not user.verify_password(password) and cp_user.verify_password(password):
        #     return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
        # 更新最后一次登录时间
        if user:
            user.update_last_seen()
            token = user.generate_user_token()
            token = get_basic_auth_str(token)
            return jsonify(re_code=RET.OK, msg='登录成功', token=token, sales_name=user.sales_name, id=user.id,
                           role_id=user.role_id)
        if cp_user:
            token = cp_user.generate_user_token()
            token = get_basic_auth_str(token)
            return jsonify(re_code=RET.OK, msg='登录成功', token=token, role_id = 1, id=84,sales_name=cp_user.CP_UserName)
    else:
        return jsonify(re_code=RET.PARAMERR, msg='图片认证超时或失败，请重新认证！')

@api.route('/cp_login', methods=['POST'])
def cp_login():
    data = request.get_json(force=True)
    username = data['username']
    password = data['password']

    # 解析Authorization
    # email, password = base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode().split(':')

    if not all([username, password]):
        return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
    try:
        cp_user = CPUser.query.filter(CPUser.CP_UserCode == username, CPUser.CP_Enable == 1).first()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(re_code=RET.DBERR, msg='查询用户失败')
    if cp_user:
        return jsonify(re_code=RET.NODATA, msg='用户不存在', user=user)
    if user == None:
        if  cp_user.verify_password(password) is not True:
            return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
    if cp_user == None:
        if  user.verify_password(password) is not True:
            return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
    # if not user.verify_password(password) and cp_user.verify_password(password):
    #     return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
    # 更新最后一次登录时间
    if cp_user:
        token = cp_user.generate_user_token()
        token = get_basic_auth_str(token)
        return jsonify(re_code=RET.OK, msg='登录成功', token=token, role_id = 1, id=84,sales_name=cp_user.CP_UserName)


@auth.verify_password
def verify_password(username_or_token, password):
    if request.path == '/cp_login':
        cp_user = CPUser.query.filter_by(email=username_or_token).first()
        if not cp_user or not cp_user.verify_password(password):
            return False
        else:
            cp_user = cp_user.verify_user_token(username_or_token)
            if not user:
                return False
            g.user = user
    return True


@auth.verify_password
def verify_password(username_or_token, password):
    if request.path == '/login':
        user = User.query.filter_by(username=username_or_token).first()
        cp_user = CPUser.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            cp_user = CPUser.query.filter_by(username=username_or_token).first()
            if not cp_user or not cp_user.verify_password(password):
                return False
            return False
    else:
        user = User.verify_user_token(username_or_token)
        cp_user = CPUser.verify_user_token(username_or_token)
        if not user and not cp_user:
            return False
        else:
            if user:
                g.user = user
            if cp_user:
                g.cp_user = cp_user
            return True



@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 201)




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
    '''获取最新定位
       入参：
           imei
       数据格式：
            [{'imei':},{}.....]
            支持一次查询多条数据
       出参：
           [{"addr":"",  # 地址
           "bLatitude":, # 纬度
           "bLongitude":,# 经度
           "devId":"",   # 所查询的设备码
           "speed":,     # 当前速度
           'type':,      #  定位类型，0表示GPS，2表示LBS
           "time":""},{}....]
       '''

    if request.method == 'POST':
        imei = request.get_json(force=True)
        a = Models.get_last_position(imei)
        c = jsonify(a)
        return c


@api.route('/get_devices_info/', methods=['POST'])
@auth.login_required
def devices_info(imei=None):
    '''获取设备信息
    入参:
        imei(设备码)
    数据格式：
        [{'imei':''},{}...]
    出参：
        [{"Device_Status":"",   #  设备状态，离线，在线，休眠
        "devId":"",             #  查询的设备码
        "gsmLevel":"",          #  基站信号强度
        "lithium":"",           #  当前电量
        "temperature":"",       #  当前温度(三代稳定控设备才有值),默认为’null‘
        "time":""},{}.....      #  数据上传时间
        ]
    '''
    if request.method == 'POST':
        imei = request.get_json(force=True)
        # type2, type3 = Models.distinguish_devices_type(imei)
        # a = Models.get_devices_info3(type2=type2, type3=type3)
        # c = jsonify(a)
        print(imei)
        a = my_info(imei)
        c = jsonify(a)
        return c


@api.route('/get_msg/', methods=['POST'])
@auth.login_required
def Get_msg():
    '''获取短信内容
    入参：
        Index_Code      # 订单号
        Index_PactCode  # 合同号
        Company_name    # 订单所属公司
        id              # 登录用户id
    数据格式：
        {
        'Index_Code':'',
        'Index_PactCode':'',
        'Company_name':''，
        'id':''
        }
    返回值：
        [{"send_location":,  #  短信发送时经纬度
        "send_time":"",      #  短信发送时间
        "sms_content":"",    #  短信类容
        "type":              #  短信类型，1表示出发短信，2表示预到达短信
        }]
    '''
    if request.method == 'POST':
        data = request.get_json(force=True)
        Index_Code = request.json.get('Index_Code')
        Index_PactCode = request.json.get('Index_PactCode')
        Company_name = request.json.get('Company_name')
        if not all([Company_name, Index_Code, Index_PactCode]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        else:
            CustomerSymbolName = models.get_CustomerSymbolName(Index_Code)
            a = Models.get_msg_info(Company_name=Company_name, Index_PactCode=Index_PactCode, Index_Code=Index_Code,CustomerSymbolName= CustomerSymbolName)
            l = jsonify(a)
        return l


@api.route('/get_pactcode/', methods=['POST'])
@auth.login_required
def Get_Pactcode():
    '''

    @return:
    '''
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
    '''获取当前登录销售旗下所有设备信息
    入参：
        page ： 当前展示的每页最大条数
        size :  当前页数
        id   :  当前用户登录ID
    参数格式：
        {"page":,
        "size":,
        "id":""
        }
    出参：
        {
        "BJ": [{
            "Companys": [{
                "Company_Id": "",             # 公司ID
                "Company_Name": "",           # 公司名字
                "IMEI": [{'Devices':},{}...], # 设备码
                "Total":                      # 设备总数
            },{}..],
            "Sales_name": "",                 # 所属销售
            "Total":                          # 属于该销售名下公司总数
        }],'SH':[],'ZX':[]}                   # BJ表示北京地区  SH表示上海地区 ZX 表示直销 [] 内部数据格式同上
    '''
    if request.method == 'POST':
        data = request.get_json(force=True)
        a = models.get_all_imei(id=int(data['id']))
        c = jsonify(a)
        return c


@api.route('/search_imei_info/', methods=['POST'])
@auth.login_required
def Search_imei_info():
    '''获取所以设备详情
    入参：
        page：     #  当前页数
        size：     #  每页数据显示数量
        id：       #  当前登录用户的ID
        type：     #  0表示查询所有，1表示查询7天内即将过期的设备
                      2表示查询60天内即将过期的设备 3表示查询已经过去的设备，4表示查询租赁设备
    数据格式：
        {
        'page':'',                  # 必传
        'size':'',                  # 必传
        'role_id':'',               # 必传
        'type':'',                  # 必传
        'Company_Name':'',          # 可传  作为搜索指定数据使用
        'Device_IMEICode':'',       # 可传  作为搜索指定数据使用
        'Sales_name':'',            # 可传  作为搜索指定数据使用
        }
    返回值：
        {"Seven":,  # 7天内即将过期的设备数量
        "Sixty":,   # 60天内即将过期的设备数量
        "datalist":[{"Company_ID":,              #  设备所属公司ID
                    "Company_Name":"",           #  设备所属公司名字
                    "Device_Expiry_Endtime":" ", #  设备过期时间
                    "Device_IMEICode":"",        #  设备IMEI编码
                    "Device_InsertTime":"",      #  设备登记时间
                    "Device_Status":"",          #  设备状态
                    "Sales_name":"",             #  所属销售姓名
                    "lithium":                   #  设备当前电量
                    'Device_OwnerType':          #  设备是否为租赁，0表示自有，1表示租赁
                    },{}...],
        "expire":,      # 已过期设备
       "total":  ,      # 设备总数
       "search_total"   # 搜索时查询到的设备总数
       }

    '''
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = request.json.get('page')
        size = request.json.get('size')
        id = request.json.get('role_id')
        type = request.json.get('type')
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
    ''' 设备详情
   入参：
        temperature： # 是否查询温控设备，0表示否，1表示查温控设备
        page：        #  当前页数
        size：        #  每页数据显示数量
        id:           #  当前用户ID
        Company_Name: #  非必传，用于搜索指定公司的设备
        IMEI:         #  非必传，用于搜索指定IMEI的设备
        Sales_name:   #  非必传，用于搜索指定销售的设备
   数据格式：
           {
           "temperature":,
            "page":,
            "size":,
            "id":""
            }
   出参：
        {
	        "count": ,                  #  设备总数
	        "list": [{
                "Company_ID": ,         #  设备所属公司ID
                "Company_Name": ,       #  设备所属公司名字
                "Device_IMEICode": ,    #  设备IMEI码
                "Device_Status": ,      #  设备状态，在线、离线、休眠
                "Sales_name": ,         #  所属销售名字
                "charging":             #  充电状态，1表示充电，0表示未充电
                "gsmLevel": ,           #  信号强度
                "lithium":              #  电池电量
                "temperature":          #  设备温度
                },{}...]
	    }
   '''
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
        ip = request.headers['X-Real-Ip']
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
        ip = request.headers['X-Real-Ip']
        return c


@api.route('/search_pactcode/', methods=['POST'])
@auth.login_required
def search_pactcode_by_imei():
    '''
    入参：
        PactCode      # 非必传 用于搜索指定合同号的订单
        Company_Name  # 非必传 用于搜索指定公司的订单
        IMEI          # 非必传 用于搜索绑定指定IMEI的订单
        page          # 当前页码
        size          # 每页显示条数
        id            # 当前用户登录ID
    参数格式：
        {"PactCode":"","Company_Name":"","IMEI":"","page":,"size":,"id":""}
    出参：
        {"count":,                      #  订单总数
        "datalist":[
                {"Company_ID":,         #  订单所属公司ID
                "Company_Name":"",      #  订单所属公司名字
                "Index_Code":"",        #  订单编码
                "Index_DeviceCode":"",  #  订单绑定的设备码
                "Index_FromTime":"",    #  订单出发时间
                "Index_PactCode":"",    #  订单合同号
                "Index_ToTime":"",      #  订单到达时间
                "Order_Status":         #  订单状态，订单状态,-1草稿,0新单据,1待调度, 2待签收,4待回单,8待结账,16已结账,32已关闭
                },{}...]}
    '''
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = data['page']
        size = data['size']
        id = int(data['id'])
        d = search_pactcode_by_imei2(data, page, size, id)
        c = jsonify(d)
        return c


# @api.route('/assignment_company', methods=['POST'])  # 给销售分配公司
# @auth.login_required
# def assignment_company():
#     '''分配公司
#     入参：
#         Company_ClientCode  # 公司编码,可以从CP查询
#         Sales_Company       # 需要划分的销售区域
#         role_id             # 登录用的role_id
#         username            # 用户账号
#         id                  # 登录用户id
#         Contacts            # 公司联系号码
#         Parent_level        # 所属父级
#     数据格式：
#         {
#         "Company_ClientCode":"",
#         "Sales_Company":"",
#         "role_id":,
#         "username":"",
#         "id":""，
#         "Contacts":""，
#         "Parent_level":""
#         }
#     出参：
#         {'res': "该用户不存在!", "code": -201}
#         {'res': "该公司不存在!", "code": -202}
#         {'res': "该销售区域不存在!", "code": -203}
#         {'res': "该公司已分配!", "code": -204}
#         {'res': "分配失败!", "code": -205}
#         {'res': "'分配成功'!", "code": 200}
#     '''
#     if request.method == 'POST':
#         ip = request.headers['X-Real-Ip']
#         data = request.get_json(force=True)
#         Company_ClientCode = request.json.get('Company_ClientCode')
#         role_id = request.json.get('role_id')
#         Sales_Company = request.json.get('Sales_Company')
#         if Sales_Company =='客户管理部(上海南软)':
#             Sales_Company =='上海'
#         elif Sales_Company =='市场部(北京)':
#             Sales_Company == '北京'
#         Parent_level = request.json.get('Parent_level')
#         if not all([Company_ClientCode, role_id, Sales_Company]):
#             return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
#         if role_id != 1:
#             return jsonify(re_code=RET.DBERR, msg='权限不足')
#         else:
#             res = models.assignment_company(data,ip=ip)
#         return jsonify(res)

@api.route('/assignment_company/', methods=['POST'])  # 给销售分配公司
@auth.login_required
def assignment_company2():
    '''分配公司
    入参：
        Company_ClientCode  # 公司编码,可以从CP查询
        Sales_Company       # 需要划分的销售区域
        role_id             # 登录用的role_id
        username            # 用户账号
        id                  # 登录用户id
        Contacts            # 公司联系号码
        Parent_level        # 所属父级
    数据格式：
        {
        "Company_ClientCode":"",
        "Sales_Company":"",
        "role_id":,
        "username":"",
        "id":""，
        "Contacts":""，
        "Parent_level":""
        }
    出参：
        {'res': "该用户不存在!", "code": -201}
        {'res': "该公司不存在!", "code": -202}
        {'res': "该销售区域不存在!", "code": -203}
        {'res': "该公司已分配!", "code": -204}
        {'res': "分配失败!", "code": -205}
        {'res': "'分配成功'!", "code": 200}
    '''
    if request.method == 'POST':
        ip = request.headers['X-Real-Ip']
        data = request.get_json(force=True)
        role_id = request.json.get('role_id')
        if role_id != 1:
            return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            res = models.assignment_company2(data,ip=ip)
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
    '''修改账户属性
    入参：
        user_id     #  需要修改的账户的user_id
        password    #  需要修改的账号密码
        is_disable  #  是否禁用，1表示是，0表示否
        type        #  1表示修改密码，2表示禁用账户
        role_id     #  登录账户的role_id
        id          #  登录账户的id
    数据格式：
        {"user_id":,"password":"","is_disable":0,"type":1,"role_id":,"id":}
        {"user_id":,"password":"","is_disable":0,"type":2,"role_id":,"id":}
    出参：
        修改成功/修改失败
    '''
    if request.method == 'POST':
        Sales_Set_Log = models.SalesSetLog()
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        is_disable = request.json.get('is_disable')
        password = request.json.get('password')
        role_id = request.json.get('role_id')
        user_id = request.json.get('user_id')
        username = request.json.get('username')
        salesaccount= request.json.get('salesaccount')
        useraccount = request.json.get('useraccount')
        type = request.json.get('type')  # 1为改密码，2为启用禁用
        if not all([str(is_disable), str(password), role_id, user_id, type]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        if role_id != 1:
            return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            Sales_Set_Log.User_Name = salesaccount
            res = models.set_account_properties(data)
            Sales_Set_Log.Creator_Name = useraccount
            Sales_Set_Log.Insert_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        username = request.json.get('username')
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
def get_elc():
    '''获取电量
    入参：
        startTime  # 查询开始时间
        endTime    # 查询结束时间
        imei       # 需要查询的设备IMEI
        page       # 当前页数
        size       # 每页显示条数
        id         # 当前登录用户id
    数据格式：
        {"startTime":,
        "endTime":,
        "imei":,
        "page":,
        "size":,
        "id":""
        }
    出参：
        {
            "count":'',     # 数据总数
            "datalist":[
            {'lithium': '', # 电量
            'time': ''      # 数据上传时间
            },{},....]
        }
    '''
    if request.method == 'POST':
        data = request.get_json(force=True)
        if len(data['imei']) == 15:
            if data['imei'][8] == '6':
                a = Models.get_elc_type3(data['imei'], start=data['startTime'], end=data['endTime'], page=data['page'],
                                         size=data['size'])
                c = jsonify(a)
            else:
                a = Models.get_elc_type2(data['imei'], start=data['startTime'], end=data['endTime'], page=data['page'],
                                         size=data['size'])
                c = jsonify(a)
            return c
        else:
            return {'res':'参数错误','code':-1001}


@api.route('/change_sales_company/', methods=['POST'])
@auth.login_required
def change_sales_company():
    '''修改所属公司
    入参：
        Company_Id  # 公司ID
        disable     # 禁用或者启用公司，0表示启用，1表示禁用
        id          # 当前登录公司ID
        user_name   # 销售账户
    数据格式：
        {"Company_Id":,
        "disable":,
        "id":"",
        'user_name':''
        }
    出参：
        {"result":""}
    '''
    if 'X-Real-Ip' in request.headers.keys():
        ip = request.headers['X-Real-Ip']
    else:
        ip = request.remote_addr
    Sales_Set_Log = models.SalesSetLog()
    if request.method == 'POST':
        data = request.get_json(force=True)  # Company_Id, user_id=None, disable=0,
        if data['disable'] == 0: # 变更归属
            a,b = models.change_sales_company(Company_Id=data['Company_Id'], user_name=data['user_name'],disable=data['disable'])
            Sales_Set_Log.User_Name = data['user_name']
            Sales_Set_Log.Creator_Name = data['useraccount']
            Sales_Set_Log.Insert_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Sales_Set_Log.IP = ip
            Sales_Set_Log.Last_Sales = b
            Company_Name = TMSSale.query.filter(TMSSale.Company_Id == data['Company_Id']).first().Company_Name
            Sales_Set_Log.Company_ID = data['Company_Id']
            Sales_Set_Log.Content = '{}在{},将{}(公司名)所属销售变更为{},操作所在地IP为:{}。'.format(Sales_Set_Log.Creator_Name,
                                                                                  Sales_Set_Log.Insert_Time,
                                                                                  Company_Name, data['user_name'], ip)
        else:  # 禁用设备
            a,b = models.change_sales_company(Company_Id=data['Company_Id'], disable=data['disable'])
            user_id = TMSSale.query.filter(TMSSale.Company_Id == data['Company_Id']).first().user_id
            Sales_Set_Log.User_Name = data['user_name']
            Sales_Set_Log.Creator_Name = data['useraccount']
            Sales_Set_Log.Insert_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
def get_sales_log():
    '''获取操作日志
    入参：
        page        # 当前页
        size        # 每页显示条数
        role_id     # 当前登录用户role_id
        username    # 需要获取的用户账户
        id          # 当前登录用的id
    数据格式：
        {"page":,"size":,"role_id":,"username":"","id":""}
    出参：
        {"datalist":[{
        "content":,    # 日志内容
        "ip":          # 操作时ip
        },{}....]}
    '''
    if request.method == 'POST':
        data = request.get_json(force=True)
        page = data['page']
        size = data['size']
        username = data['username']
        salesaccount = data['salesaccount']
        role_id = data['role_id']
        print(data)
        if not all([page, size, username, role_id]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        # if role_id !=1:
        #     return jsonify(re_code=RET.DBERR, msg='权限不足')
        else:
            a = models.get_sales_log(salesaccount=salesaccount, page=data['page'], size=data['size'])
            c = jsonify(a)
        return c


@api.route('/renew_device/', methods=['POST'])
@auth.login_required
def renew_device():
    '''设备续租
    入参：
        end_time  # 到期时间
        user_id   # 操作用的user_id
        imei      # 操作的设备码
    数据格式：
        {"end_time":"2020-04-03 12:00:00","user_id":"23","imei":"351608086033268"}
    出参：
        {"result":""}
    '''
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        end_time = data['end_time']
        imei = data['imei']
        user_id = int(data['user_id'])
        username = data['username']
        useraccount = data['useraccount']
        if not all([user_id, imei, end_time]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        else:
            a = models.renew_device(user_id=data['user_id'], imei=data['imei'], end_time=data['end_time'],
                                    ip=ip,username=username,useraccount=useraccount)
            c = jsonify(a)
        return c


@api.route('/get_msg_count/', methods=['POST'])
@auth.login_required
def get_msg_count():
    '''获取短信总数
    入参:
        end_time    # 查询时间，输入每月1号，自动获取1个月短信数据
        user_id     # 当前登录用户的user_id
    数据格式：
        da = {"user_id":23,'end_time':'2019-01-01'}
    出参：
         整数
    '''
    if request.method == 'POST':
        data = request.get_json(force=True)
        end_time = data['end_time']
        user_id = int(data['id'])
        if not all([user_id, end_time]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        else:
            a = models.get_msg_count(user_id=data['id'], day_now=data['end_time'])
            c = jsonify(a)
        return c


@api.route('/set_company_name/', methods=['POST'])
@auth.login_required
def update_set_company_name():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        set_name = Set_Name(data=data, ip=ip)
    executor.submit(set_company_name,data,ip)
    return {'res':'处理中,请1分钟后查看结果！'}

def set_company_name(data, ip):
    set_name = Set_Name(data=data, ip=ip)
    set_name.send_set_name_cmd()

@api.route('/set_name_list/', methods=['POST'])
@auth.login_required
def set_name_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        set_name = Set_Name(data=data,ip = ip)
        a = set_name.get_set_name_result()
        c = jsonify(a)
        return c

@api.route('/get_sales_tree/', methods=['POST'])
@auth.login_required
def get_sales_tree():
    if request.method == 'POST':
        data = request.get_json(force=True)
        set_name = sales_tree(data=data)
        a = set_name.data_control()
        c = jsonify(a)
        return c

@api.route('/edit_department/', methods=['POST'])
@auth.login_required
def edit_department():
    if request.method == 'POST':
        data = request.get_json(force=True)
        edit_department = Edit_deppart(data=data)
        a = edit_department.data_control()
        c = jsonify(a)
        return c

@api.route('/sales_company_info/', methods=['POST'])
@auth.login_required
def sales_company2():
    if request.method == 'POST':
        data = request.get_json(force=True)
        s = sales_company(args=data)
        a = s.get_company_list()
        c = jsonify(a)
        return c


@api.route('/search_sales_tree/', methods=['POST'])
@auth.login_required
def search_sales_tree():
    if request.method == 'POST':
        data = request.get_json(force=True)
        s = Search_sales_tree(data=data)
        a = s.data_control()
        c = jsonify(a)
        return c

@api.route('/get_company_name/', methods=['POST'])
@auth.login_required
def get_company_name():
    if request.method == 'POST':
        data = request.get_json(force=True)
        s = Search_sales_tree(data=data)
        a = s.search_company_name()
        c = jsonify(a)
        return c

@api.route('/get_more_postion/', methods=['POST'])
@auth.login_required
def get_more_postion():
    if request.method == 'POST':
        data = request.get_json(force=True)
        s = More_Position(data=data)
        a = s.get_more_position()
        c = jsonify(a)
        return c

@api.route('/get_all_stock/', methods=['POST'])
@auth.login_required
def get_all_stock():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.get_all_stock()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/get_all_sales/', methods=['POST'])
@auth.login_required
def get_all_sales():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.get_all_sales()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/add_stock/', methods=['POST'])
@auth.login_required
def add_stock():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.add_stock()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/init_stock/', methods=['POST'])
@auth.login_required
def init_stock():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.init_stock()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/set_sale_status/', methods=['POST'])
@auth.login_required
def set_sale_status():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.set_sale_status()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/set_disable_status/', methods=['POST'])
@auth.login_required
def set_disable_status():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.set_disable_status()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/get_set_log/', methods=['POST'])
@auth.login_required
def get_set_log():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.get_set_log()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/get_disable_devices/', methods=['POST'])
@auth.login_required
def get_disable_devices():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.get_disable_devices()
        c = jsonify(a)
        s.close_conn()
        return c
@api.route('/renew_flow_fee/', methods=['POST'])
@auth.login_required
def renew_flow_fee():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data, ip=ip)
        if 'end_time' in data[0].keys():
            a = s.renew_flow_fee()
            c = jsonify(a)
        else:
            a = s.change_sales()
            c = jsonify(a)
        s.close_conn()
        return c

@api.route('/get_remarks/', methods=['POST'])
@auth.login_required
def get_remarks():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.get_remarks()
        c = jsonify(a)
        s.close_conn()
        return c
@api.route('/get_expiring_soon/', methods=['POST'])
@auth.login_required
def get_expiring_soon():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = device_stock(data=data,ip=ip)
        a = s.get_expiring_soon()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route("/get_img/",methods=['POST'])
def get_img():
    a = getAuthImage()
    c = jsonify(a)
    return c

@api.route("/ver_code/",methods=['POST'])
def ver_code():
    data = request.get_json(force=True)
    uid = data['uid']
    move_x = data['x']
    move_y = data['y']
    a = AuthImage(uid=uid,move_x=move_x,move_y=move_y)
    c = jsonify(a)
    return c

# @api.route("/exp_excel/",methods=['GET'])
# def exp_excel():
#     q = db.session.query(
#         models.TMSDevice.Device_IMEICode.label('设备编码'),
#         models.TMSDevice.Device_PhoneNo.label('设备号码'),
#         models.TMSDevice.Device_SIMid.label('SIM提供商'),
#         models.TMSDevice.Device_IMSI.label('IMSI码'),
#         models.TMSDevice.Device_OwnerType.label('租用状态'),
#         models.TMSDevice.Device_Type.label('设备类型'),
#         models.TMSDevice.Device_temperature.label('是否温控'),
#     ).order_by(models.TMSDevice.Device_InsertTime.desc())
#     query_sets = q.all()
#     return excel.make_response_from_query_sets(
#         query_sets,
#         coTlumn_names=[
#             '设备编码',
#             '设备号码',
#             'SIM提供商',
#             'IMSI码',
#             '租用状态',
#             '设备类型',
#             '是否温控',
#         ],
#         file_type='xlsx',
#         file_name='list.xlsx')

@api.route('/get_all_device/', methods=['POST'])
@auth.login_required
def get_all_Device1():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        # s = Set_Device_Comapy(data=data,ip=ip)
        # a = s.get_all_Device22()
        a = get_all_device(data)
        c = jsonify(a)
        return c

@api.route('/add_devices/', methods=['POST'])
@auth.login_required
def add_devices():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.add_devices()
        c = jsonify(a)
        return c

@api.route('/device_check/', methods=['POST'])
@auth.login_required
def device_check():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.device_check()
        c = jsonify(a)
        return c

@api.route('/get_all_company_name/', methods=['POST'])
@auth.login_required
def get_all_company_name():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.get_all_company_name()
        c = jsonify(a)
        return c

@api.route('/set_devices_status/', methods=['POST'])
@auth.login_required
def set_devices_status():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.set_devices_status()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/get_receipt_company_log/', methods=['POST'])
@auth.login_required
def get_receipt_company_log():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.get_receipt_company_log()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/get_receipt_log/', methods=['POST'])
@auth.login_required
def get_receipt_Log():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.get_receipt_Log()
        c = jsonify(a)
        s.close_conn()
        return c
@api.route('/batch_disable/', methods=['POST'])
@auth.login_required
def batch_disable():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.batch_disable()
        c = jsonify(a)
        s.close_conn()
        return c
@api.route('/change_imsi/', methods=['POST'])
@auth.login_required
def change_imsi():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.change_imsi()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/change_owner_type/', methods=['POST'])
@auth.login_required
def change_owner_type():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.change_owner_type()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/get_top_order/', methods=['POST'])
@auth.login_required
def get_top_order():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        a = get_top_order(data['pacthCode'])
        c = jsonify(a)
        return c

@api.route('/ex_port/', methods=['POST'])
@auth.login_required
def ex_port_excel():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        set_device_comapy = Set_Device_Comapy(data=data, ip=ip)
        set_device_comapy.excel_ctrl()
        executor.submit(ex_port,data,ip)
        return {'res':'处理中,请稍后查看结果！'}

def ex_port(data, ip):
    set_device_comapy = Set_Device_Comapy(data=data, ip=ip)
    set_device_comapy.excel_ctrl()

@api.route('/ex_port/', methods=['POST'])
@auth.login_required
def get_all_excel_list():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        set_device_comapy = Set_Device_Comapy(data=data, ip=ip)
        set_device_comapy.excel_ctrl()
        executor.submit(ex_port,data,ip)
        return {'res':'处理中,请稍后查看结果！'}


my_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
download_path = os.path.join(my_path, 'download')
@api.route("/download/<path:filename>")
# @auth.login_required
def downloader(filename):
    download_path
    return send_from_directory(download_path,filename,as_attachment=True)


@api.route('/get_mp/', methods=['POST'])
def get_mp():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['code'] =='qwer?1234!@#1312':
            s = More_Position(data=data)
            a = s.get_more_position()
            c = jsonify(a)
            return c

@api.route('/get_lg/', methods=['POST'])
def get_lg():
    if request.method == 'POST':
        data = request.get_json(force=True)
        l=[]
        if data['code'] =='qwer?1234!@#1312':
            for i in data['datalist']:
                s = get_ln(patcode=i['patcode'],imei=i['imei'])
                l.append(s)
        c = jsonify(l)
        return c

@api.route('/get_test_elc/', methods=['POST'])
def get_test_elc():
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)
        if data['code'] =='qwer?1234!@#1312':
            s = Models.get_test_last_position(data['imei'])
            c = jsonify(s)
            return c

@api.route('/get_test_hbt/', methods=['POST'])
def get_test_hbt():
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)
        if data['code'] =='qwer?1234!@#1312':
            s = Models.get_elc(data['imei'])
            c = jsonify(s)
            return c

@api.route('/get_order_res/', methods=['POST'])
def get_order_res():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['code'] =='qwer?1234!@#1312':
            s = Models.get_order_res(imei=data['imei'],tag =data['tag'])
            c = jsonify(s)
            return c

@api.route('/get_test_ln/', methods=['POST'])
def get_test_ln():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['code'] =='qwer?1234!@#1312':
            s = get_ln2(patcode=data['patcode'],imei=data['imei'])
            c = jsonify(s)
            return c

@api.route('/get_test_info/', methods=['POST'])
def get_test_info():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['code'] == 'qwer?1234!@#1312':
            s = Models.get_info(imei=data['imei'], tag=data['tag'])
            c = jsonify(s)
            return c

@api.route('/get_test_mp/', methods=['POST'])
def get_test_mp():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['code'] =='qwer?1234!@#1312':
            s = More_Position(data=data)
            a = s.get_test_position()
            c = jsonify(a)
            return c

# @api.route('/get_top_order/', methods=['POST'])
# def get_top_order():
#     if request.method == 'POST':
#         data = request.get_json(force=True)
#         if data['code'] =='qwer?1234!@#1312':
#             a = get_top_order_info(data=data)
#             c = jsonify(a)
#             return c

@api.route('/disabled_devices/', methods=['POST'])
@auth.login_required
def disabled_devices():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = Set_Device_Comapy(data=data,ip=ip)
        a = s.disabled_devices()
        c = jsonify(a)
        s.close_conn()
        return c

@api.route('/add_register_devices/', methods=['POST'])
@auth.login_required
def add_register_devices2():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = add_register_devices(data=data)
        c = jsonify(s)
        return c

@api.route('/get_register_devices_list/', methods=['POST'])
@auth.login_required
def get_register_devices_list2():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = get_register_devices_list(data=data)
        c = jsonify(s)
        return c
@api.route('/set_register_devices_status/', methods=['POST'])
@auth.login_required
def set_register_devices_status2():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = set_register_devices_status(data=data)
        c = jsonify(s)
        return c


@api.route('/add_pos/', methods=['POST'])
def set_add_pos():
    if request.method == 'POST':
        if 'X-Real-Ip' in request.headers.keys():
            ip = request.headers['X-Real-Ip']
        else:
            ip = request.remote_addr
        data = request.get_json(force=True)
        s = add_pos(data=data)
        c = jsonify(s)
        return c


app.register_blueprint(api, url_prefix='/api')
# @api.route('/excel_download/', methods=['POST'])
# @auth.login_required
# def excel_download():
#     if request.method == 'POST':
#         ip = request.headers['X-Real-Ip']
#         data = request.get_json(force=True)
#         s = Set_Device_Comapy(data=data,ip=ip)
#         download_path = s.excel_test()
#         return send_from_directory(app.config['UPLOAD_FOLDER'],filename,as_attachment=True)


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0',  # 设置ip，默认127.0.0.1
            port=7777,  # 设置端口，默认5000
            debug=None,
            threaded=True)