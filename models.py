# coding: utf-8
# import datetime
import sys

sys.path.append("..")
import calendar
import time
import hashlib
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, Column
from sqlalchemy import or_
from sqlalchemy.orm import relationship, backref
from my_db import Models
from my_db.my_sql import open_mysql
from flask import Flask
from xpinyin import Pinyin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from flask import jsonify, current_app, g, request
from functools import wraps
from login_mode.response_code import RET
from myconfig import sqldb, mgdb, api_cfg, ere_cfg

my = open_mysql()
app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = api_cfg
app.config['SECRET_KEY'] = 'test$$$!!!!##!#!#@!@!'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['AUTH_TYPE'] = 'AUTH_REMOTE_USER'
app.config["SQLALCHEMY_BINDS"] = {'ere': ere_cfg}

db = SQLAlchemy(app)

db.init_app(app)
CORS(app, supports_credentials=True)


def get_child(id):
    k_l = []
    k_l.append(id)
    child = db.session.query(Salesarea).filter(Salesarea.parent_id == id, Salesarea.is_disable == 0).all()
    if len(child) != 0:
        for k in child:
            k_l.append(k.area_id)
    else:
        k_l.append(id)
    return k_l


global l_list
l_list = []


def find_all_child(id):
    global l_list
    l_list.append(id)
    child = db.session.query(Salesarea).filter(Salesarea.parent_id == id, Salesarea.is_disable == 0).all()
    if len(child) != 0:
        for i in child:
            l_list = l_list + get_child(i.area_id)
        return find_all_child(i.area_id)
    else:
        for k in child:
            l_list = l_list + get_child(k.area_id)
    l_list = list(set(l_list))
    return l_list


def get_all_id(id):
    u_id = db.session.query(User).filter(User.is_disable == 0, User.id == id).first()
    my_l = []
    if u_id.is_manager == 1:
        id = u_id.parent_id
        p_id = db.session.query(Salesarea).filter(Salesarea.is_disable == 0, Salesarea.area_id == id).first()
        l = find_all_child(p_id.parent_id)
        for area in l:
            rs = db.session.query(User).filter(User.is_disable == 0, User.parent_id == area).all()
            if rs:
                for k in rs:
                    my_l.append(k.id)
    else:
        my_l.append(id)
    global l_list
    l_list = []
    return my_l


class ReceiptLog(db.Model):
    __tablename__ = 'Receipt_Log'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    IMEI = db.Column(db.String(128))
    IP = db.Column(db.String(128))
    User_Name = db.Column(db.String(128))
    Content = db.Column(db.String(128))
    Set_Time = db.Column(db.DateTime, default=datetime.now)
    User_ID = db.Column(db.BigInteger)
    Creator_Name = db.Column(db.String(128))
    Company_ID = db.Column(db.BigInteger)


class User(db.Model):
    '''用户模型
    '''
    __tablename__ = 'Par_User'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    sales_name = db.Column(db.String(128))
    role_id = db.Column(db.Integer, default=0)
    join_time = db.Column(db.DateTime, default=datetime.now)
    last_seen = db.Column(db.DateTime, default=datetime.now)
    is_disable = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, default=0)
    top_parent_id = db.Column(db.Integer, default=0)
    is_manager = db.Column(db.Integer, default=0)

    @property
    def password(self):
        raise AttributeError('密码不可访问')

    @password.setter
    def password(self, password):
        '''生成hash密码'''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        '''
        密码验证
        :param password-> 用户密码
        :return 验证成功返回True,否则返回False
        '''
        return check_password_hash(self.password_hash, password)

    def generate_user_token(self, expiration=43200):
        '''
        生成确认身份的Token(密令)
        :param expiration-> 有效期限,单位为秒/此处默认设置为12h
        :return 加密过的token
        '''
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id, 'username': self.username}).decode('utf-8')

    # 解析token，确认登录的用户身份
    @staticmethod
    def verify_user_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    # 额外的功能
    def update_last_seen(self):
        '''
        更新最后一次登录时间
        '''
        self.last_seen = datetime.now()
        db.session.add(self)

    def to_json(self):
        '''返回用户信息'''
        return {
            'user_id': self.id,
            'username': self.username,
        }

    def __repr__(self):
        return '<User %r>' % self.username

    # TODO: 可以添加用户头像


class CPUser(db.Model):
    '''用户模型
    '''
    __tablename__ = 'CP_User'
    __table_args__ = {'schema': 'WLY.dbo'}
    CP_UserId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CP_UserCode = db.Column(db.String(255), unique=True, index=True)
    CP_Password = db.Column(db.String(128))
    CP_UserName = db.Column(db.String(128))
    CP_Phone = db.Column(db.String(128))
    CP_CreateTime = db.Column(db.DateTime, default=datetime.now)
    CP_UpdateTime = db.Column(db.DateTime, default=datetime.now)
    CP_Enable = db.Column(db.Integer, default=0)
    CP_CreateId = db.Column(db.Integer, default=0)
    CP_UpdateId = db.Column(db.Integer, default=0)
    CP_CreateName = db.Column(db.String(128))
    CP_UpdateName = db.Column(db.String(128))
    CP_Department = db.Column(db.String(128))
    CP_Position = db.Column(db.String(128))
    CP_Sex = db.Column(db.Integer, default=0)

    def get_md5(self, password):
        # 待加密信息
        # 创建md5对象
        m = hashlib.md5()
        # Tips
        # 此处必须encode
        # 若写法为m.update(str)  报错为： Unicode-objects must be encoded before hashing
        # 因为python3里默认的str是unicode
        # 或者 b = bytes(str, encoding='utf-8')，作用相同，都是encode为bytes
        b = password.encode(encoding='utf-8')
        m.update(b)
        str_md5 = m.hexdigest()
        return str_md5

    @property
    def password(self):
        raise AttributeError('密码不可访问')

    @password.setter
    def password(self, password):
        '''生成hash密码'''
        self.password_hash = self.get_md5(password)

    def verify_password(self, password):
        if self.get_md5(password) == self.CP_Password:
            return True
        else:
            return False

    def generate_user_token(self, expiration=43200):
        '''
        生成确认身份的Token(密令)
        :param expiration-> 有效期限,单位为秒/此处默认设置为12h
        :return 加密过的token
        '''
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.CP_UserId, 'username': self.CP_UserCode}).decode('utf-8')

    # 解析token，确认登录的用户身份
    @staticmethod
    def verify_user_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = CPUser.query.get(data['id'])
        return user

    def to_json(self):
        '''返回用户信息'''
        return {
            'user_id': self.id,
            'username': self.username,
        }

    def __repr__(self):
        return '<User %r>' % self.username


# u = CPUser.query.filter(CPUser.CP_UserCode == 'liuyang', CPUser.CP_Enable == 1).first()
# print(u.CP_UserId)


class Order_List(db.Model):
    __tablename__ = 'Order_List'
    __table_args__ = {'schema': 'WLY.dbo'}
    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    User_ID = db.Column(db.Integer)
    Name = db.Column(db.String(128))
    Content = db.Column(db.String(128))
    IP = db.Column(db.String(128))
    Tag = db.Column(db.Integer)
    Time = db.Column(db.Integer)


class DeviceStock(db.Model):
    __tablename__ = 'Device_Stock'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    Device_IMEI = db.Column(db.String(128), primary_key=True)
    Sales_Name = db.Column(db.String(128))
    User_ID = db.Column(db.Integer)
    Company_ID = db.Column(db.Integer)
    Company_Name = db.Column(db.String(128))
    Sales_Time = db.Column(db.DateTime)
    Sales_Statues = db.Column(db.Integer, default=0)
    Device_Inserttime = db.Column(db.DateTime)
    Flow_Fee_Start_Time = db.Column(db.DateTime)
    Flow_Fee_End_Time = db.Column(db.DateTime)
    Company_ClientCode = db.Column(db.String(128))
    is_disable = db.Column(db.Integer, default=0)
    Remarks = db.Column(db.String(128))
    Remark_Time = db.Column(db.DateTime)


class SalesSetLog(db.Model):
    __tablename__ = 'Sales_Set_Log'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    Creator_Name = db.Column(db.String(128))
    IP = db.Column(db.String(128))
    Content = db.Column(db.String(128))
    Type = db.Column(db.Integer)
    Company_ID = db.Column(db.Integer)
    User_Name = db.Column(db.String(128))
    Insert_Time = db.Column(db.Integer)
    Last_Sales = db.Column(db.String(128))


class Order_Sign_Log(db.Model):
    __tablename__ = 'order_sign_log'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sms_id = db.Column(db.Integer)
    order_code = db.Column(db.String(128))
    pact_code = db.Column(db.String(128))
    root_order_id = db.Column(db.Integer)
    verify_code = db.Column(db.String(128))


# class ReceiptLog(db.Model):
#     __tablename__ = 'Receipt_Log'
#     __bind_key__ = 'ere'
#     __table_args__ = {'schema': 'ERE.dbo'}
#     ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     New_Company = db.Column(db.String(128))
#     Device_IMEI = db.Column(db.String(128))
#     Original_Company = db.Column(db.String(128))
#     InsertTime = db.Column(db.DateTime, default=datetime.now)
#     Creator_Name = db.Column(db.String(128))


class TMSCompany(db.Model):
    __tablename__ = 'TMS_Company'
    __table_args__ = {'schema': 'WLY.dbo'}
    Company_ID = db.Column(db.BigInteger, primary_key=True)
    Company_Name = db.Column(db.Unicode(300), nullable=False)
    Company_Personal = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_Industry = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_Logo = db.Column(db.Unicode(300))
    Company_Web = db.Column(db.Unicode(300))
    Company_Description = db.Column(db.Unicode)
    Company_Scale = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_Map = db.Column(db.Unicode(300))
    Company_ProvinceID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_CityID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_DistrictID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_TownID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_Keywords = db.Column(db.Unicode(200))
    Company_Contact = db.Column(db.Unicode(300))
    Company_Gender = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_Phone = db.Column(db.Unicode(100))
    Company_Status = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    Company_OfficeNo = db.Column(db.Unicode(100))
    Company_Fax = db.Column(db.Unicode(100))
    Company_Address = db.Column(db.Unicode(300))
    Company_Zip = db.Column(db.Unicode(100))
    Company_Mail = db.Column(db.Unicode(200))
    Company_ClientCode = db.Column(db.Unicode(100))
    Company_ShortName = db.Column(db.Unicode(100))
    Company_EnName = db.Column(db.Unicode(200))
    Company_ShortEnName = db.Column(db.Unicode(200))
    Company_Master = db.Column(db.Unicode(100))
    Company_License = db.Column(db.Unicode(300))
    Company_LicensePic = db.Column(db.Unicode(300))
    Company_Weixin = db.Column(db.Unicode(100))
    Company_Bank = db.Column(db.Unicode(100))
    Company_BankAccount = db.Column(db.Unicode(100))
    Company_RefereCompany = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_CreatorID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_InsertTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Company_Updater = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_UpdateTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Company_Invalid = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Company_Comments = db.Column(db.String(256, 'Chinese_PRC_CI_AS'))
    opt_status = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_IsGroup = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_IsZones = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_BillDay = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_DriversLicense = db.Column(db.String(18, 'Chinese_PRC_CI_AS'), server_default=db.FetchedValue())
    Company_DrivingLicense = db.Column(db.String(12, 'Chinese_PRC_CI_AS'), server_default=db.FetchedValue())
    Company_CardID = db.Column(db.String(18, 'Chinese_PRC_CI_AS'), server_default=db.FetchedValue())
    Company_DriversLicensePic = db.Column(db.Unicode(200), server_default=db.FetchedValue())
    Company_DrivingLicensePic = db.Column(db.Unicode(200), server_default=db.FetchedValue())
    Company_CardIDPic = db.Column(db.Unicode(200), server_default=db.FetchedValue())
    Company_Verify = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_Signtype = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_GUID = db.Column(db.Unicode(50), server_default=db.FetchedValue())
    Company_Source = db.Column(db.Integer, server_default=db.FetchedValue())
    Company_Code = db.Column(db.Unicode(50), server_default=db.FetchedValue())
    Company_Province = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_City = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_District = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_Check = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Company_BankFirst = db.Column(db.Unicode(255))
    Company_BankName = db.Column(db.Unicode(255))
    Company_VerifyTime = db.Column(db.DateTime)
    Company_InvalidCp = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Company_WorkingAddress = db.Column(db.Unicode(300))
    Company_AddressLongitude = db.Column(db.Numeric(18, 8))
    Company_AddressLatitude = db.Column(db.Numeric(18, 8))


class TMSOrderIndex(db.Model):
    __tablename__ = 'TMS_OrderIndex'
    __table_args__ = {'schema': 'WLY.dbo'}
    Index_ID = db.Column(db.BigInteger, primary_key=True)
    opt_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_Code = db.Column(db.Unicode(50), nullable=False)
    Index_PactCode = db.Column(db.Unicode(50))
    Index_EndUserID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_EndUserName = db.Column(db.Unicode(300))
    Index_From = db.Column(db.Unicode(300))
    Index_FromProvince = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_FromCity = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_FromDistrict = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_FromTime = db.Column(db.DateTime)
    Index_To = db.Column(db.Unicode(300))
    Index_ToProvince = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_ToCity = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_ToDistrict = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_ToTime = db.Column(db.DateTime)
    Index_TransportMode = db.Column(db.BigInteger)
    Index_GoodsCategory = db.Column(db.BigInteger)
    Index_PackageMode = db.Column(db.BigInteger)
    Index_ChargeMode = db.Column(db.BigInteger)
    Index_PriceUnit = db.Column(db.BigInteger)
    Index_Status = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    Index_StatusTime = db.Column(db.DateTime, nullable=False)
    Index_SrcOrderID = db.Column(db.BigInteger, index=True, server_default=db.FetchedValue())
    Index_RootOrderID = db.Column(db.BigInteger, index=True, server_default=db.FetchedValue())
    Index_SrcClass = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    Index_Kms = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_CarType = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_CarLength = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_DriverID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_CarID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_SupplierID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_SupplierCompanyID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_CustomerID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_CustomerCompanyID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_ShipMode = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_Pick = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_Delivery = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_Creator = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    Index_CreatorCompanyID = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    Index_CreateTime = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    Index_Confirmer = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_ConfirmTime = db.Column(db.DateTime)
    Index_Singer = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_SignTime = db.Column(db.DateTime)
    Index_ReceiptDoc = db.Column(db.Unicode(512))
    Index_Exception = db.Column(db.Unicode(512), server_default=db.FetchedValue())
    Index_Invalid = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_Comments = db.Column(db.String(256, 'Chinese_PRC_CI_AS'))
    Index_OnLoad = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_OffLoad = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_Insurance = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_VolumeAddition = db.Column(db.Numeric(18, 6), server_default=db.FetchedValue())
    Index_WeightAddition = db.Column(db.Numeric(18, 4), server_default=db.FetchedValue())
    Index_Description = db.Column(db.Unicode, server_default=db.FetchedValue())
    Index_CarVolume = db.Column(db.Numeric(18, 6), server_default=db.FetchedValue())
    Index_CarWeight = db.Column(db.Numeric(18, 4), server_default=db.FetchedValue())
    Index_Combined = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_CustomerSymbolID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_SupplierSymbolID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_ReceiptDoc1 = db.Column(db.Unicode(512))
    Index_ReceiptDoc2 = db.Column(db.Unicode(512))
    Index_ReceiptDoc3 = db.Column(db.Unicode(512))
    Index_FromContact = db.Column(db.Unicode(300))
    Index_ToContact = db.Column(db.Unicode(300))
    Index_GoodsValue = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_PrevOrderID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_DeviceCode = db.Column(db.Unicode(50))
    Index_Payment = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_Payable = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_GoodsLst = db.Column(db.Unicode)
    Index_RealFromTime = db.Column(db.DateTime)
    Index_RealToTime = db.Column(db.DateTime)
    Index_ReceiptDoc4 = db.Column(db.Unicode(512))
    Index_ReceiptDoc5 = db.Column(db.Unicode(512))
    Index_ReceiptDoc6 = db.Column(db.Unicode(512))
    Index_ReceiptDoc7 = db.Column(db.Unicode(512))
    Index_ReceiptDoc8 = db.Column(db.Unicode(512))
    Index_ReceiptDoc9 = db.Column(db.Unicode(512))
    Index_FromOperator = db.Column(db.Unicode(100))
    Index_TerminalOrderID = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_TerminalOrderCode = db.Column(db.Unicode(100))
    Index_CustomerName = db.Column(db.Unicode(300), server_default=db.FetchedValue())
    Index_SupplierName = db.Column(db.Unicode(300), server_default=db.FetchedValue())
    Index_CreatorCompanyName = db.Column(db.Unicode(300), server_default=db.FetchedValue())
    Index_CustomerSymbolName = db.Column(db.Unicode(300), server_default=db.FetchedValue())
    Index_SupplierSymbolName = db.Column(db.Unicode(300), server_default=db.FetchedValue())
    Index_TotalCost = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_TotalAmount = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_TotalWeight = db.Column(db.Numeric(18, 4), server_default=db.FetchedValue())
    Index_TotalVolume = db.Column(db.Numeric(18, 6), server_default=db.FetchedValue())
    Index_BeSplit = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_SplitType = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_CombinedAmount = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_CombinedCost = db.Column(db.Numeric(18, 2), server_default=db.FetchedValue())
    Index_CombinedWeight = db.Column(db.Numeric(18, 4), server_default=db.FetchedValue())
    Index_CombinedVolume = db.Column(db.Numeric(18, 6), server_default=db.FetchedValue())
    Index_CombinedOrderAmount = db.Column(db.BigInteger, server_default=db.FetchedValue())
    Index_CombinedFrom = db.Column(db.Unicode(300), server_default=db.FetchedValue())
    Index_CombinedTo = db.Column(db.Unicode(300), server_default=db.FetchedValue())
    Index_TCacheReady = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_StartMsgTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Index_ArriveMsgTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Index_VerifyCode = db.Column(db.String(6, 'Chinese_PRC_CI_AS'), server_default=db.FetchedValue())
    Index_DeviceCreatTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Index_GPSStartTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Index_DeviceBindingTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Index_FromLocation = db.Column(db.String(50, 'Chinese_PRC_CI_AS'), server_default=db.FetchedValue())
    Index_ToLocation = db.Column(db.String(50, 'Chinese_PRC_CI_AS'), server_default=db.FetchedValue())
    Index_ContainsBillDay = db.Column(db.DateTime, server_default=db.FetchedValue())
    Index_TrackType = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_Fromtype = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_Totype = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_RollBack = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_CusRollBack = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_tpPrint = db.Column(db.String(200, 'Chinese_PRC_CI_AS'), server_default=db.FetchedValue())
    Index_GUID = db.Column(db.Unicode(50), server_default=db.FetchedValue())
    Index_FromManID = db.Column(db.Integer)
    Index_FromMan = db.Column(db.Unicode(50))
    Index_ToManID = db.Column(db.Integer)
    Index_ToMan = db.Column(db.Unicode(50))
    Index_RollBackOrderID = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    Index_ReceipTime = db.Column(db.DateTime)
    Index_ExceptionType = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_AssessLevel = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_AssessMent = db.Column(db.Unicode(200), server_default=db.FetchedValue())
    Index_CloseMark = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_CloseMent = db.Column(db.Unicode(100), server_default=db.FetchedValue())
    Index_Addorder = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_AddPacth = db.Column(db.Unicode(200), server_default=db.FetchedValue())
    Index_CarCount = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_AutoSchedule = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_CombinePrice = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_OrderType = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_SupplierType = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_CloseInitiator = db.Column(db.Unicode(100))
    Index_CloseType = db.Column(db.BigInteger)
    Index_signinfotype = db.Column(db.Integer, server_default=db.FetchedValue())
    Index_signinfo = db.Column(db.Unicode)
    Index_RollBckLst = db.Column(db.Unicode, server_default=db.FetchedValue())
    Index_VerifySiginTime = db.Column(db.DateTime, server_default=db.FetchedValue())
    Index_CreateType = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    Index_ReceiptType = db.Column(db.Integer)
    Index_additionTransportType = db.Column(db.Unicode(1))
    Index_DeviceCode2 = db.Column(db.Unicode(255))
    Index_Distance = db.Column(db.Numeric(18, 2))
    Index_RealFromStatus = db.Column(db.Integer)
    Index_WithChildType = db.Column(db.Integer)


class TMSSale(db.Model):
    __tablename__ = 'TMS_Sales'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    Sales_Id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    # user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    Sales_name = db.Column(db.String(255, 'Chinese_PRC_CI_AS'))
    Company_Id = db.Column(db.Integer)
    Company_Name = db.Column(db.String(255, 'Chinese_PRC_CI_AS'))
    Sales_Company = db.Column(db.String(255, 'Chinese_PRC_CI_AS'))
    Bind_time = db.Column(db.DateTime)
    Is_disabled = db.Column(db.Integer)
    Contacts = db.Column(db.String(255, 'Chinese_PRC_CI_AS'))
    Parent_level = db.Column(db.String(255, 'Chinese_PRC_CI_AS'))


class TMSDevice(db.Model):
    __tablename__ = 'TMS_Devices'
    __table_args__ = {'schema': 'WLY.dbo'}
    Device_ID = db.Column('Device_ID', db.BigInteger, nullable=False, index=True, primary_key=True)
    Device_IMEICode = db.Column('Device_IMEICode', db.Unicode(50), nullable=False)
    Device_CompanyID = db.Column('Device_CompanyID', db.BigInteger)
    Device_Invalid = db.Column('Device_Invalid', db.Integer, server_default=db.FetchedValue())
    Device_Expiry_Starttime = db.Column('Device_Expiry_Starttime', db.DateTime)
    Device_Expiry_Endtime = db.Column('Device_Expiry_Endtime', db.DateTime)
    Device_Type = db.Column('Device_Type', db.Integer, nullable=False)
    Device_InsertTime = db.Column('Device_InsertTime', db.DateTime)
    Device_temperature = db.Column('Device_temperature', db.Integer)
    Device_OwnerType = db.Column('Device_OwnerType', db.Integer)
    Device_PhoneNo = db.Column('Device_PhoneNo', db.String(128))
    Device_SIMid = db.Column('Device_SIMid', db.Integer)
    Device_IMSI = db.Column('Device_IMSI', db.String(128))
    Device_SIMBatch = db.Column('Device_SIMBatch', db.String(128))
    Device_SalerName = db.Column('Device_SalerName', db.String(128))
    Device_Comments = db.Column('Device_Comments', db.String(128))
    Device_Creator = db.Column('Device_Creator', db.Integer)


class TMSOrderIndexSms(db.Model):
    __tablename__ = 'TMS_OrderIndex_Sms'
    __table_args__ = {'schema': 'WLY.dbo'}
    Index_Id = db.Column('Index_Id', db.BigInteger, nullable=False, index=True, primary_key=True)
    Index_Code = db.Column('Index_Code', db.String(128), nullable=False)
    Index_PactCode = db.Column('Index_PactCode', db.String(128))
    Index_FromProvince = db.Column(db.Integer)
    Index_FromCity = db.Column(db.Integer)
    Index_FromDistrict = db.Column(db.Integer)
    Index_ToProvince = db.Column(db.Integer)
    Index_ToCity = db.Column(db.Integer)
    Index_ToDistrict = db.Column(db.Integer)
    Index_FromTime = db.Column(db.DateTime)
    Index_ToTime = db.Column(db.DateTime)
    Index_Status = db.Column(db.Integer)
    Index_FromLocation = db.Column(db.String(128))
    Index_ToLocation = db.Column(db.String(128))
    Index_RootOrderID = db.Column(db.Integer)
    Index_Fromtype = db.Column(db.Integer)
    Index_Totype = db.Column(db.Integer)
    Index_StartMsgTime = db.Column(db.DateTime)
    Index_ArriveMsgTime = db.Column(db.DateTime)
    Index_DeviceCode = db.Column(db.String(128))
    Index_DeviceBindingTime = db.Column(db.DateTime)
    Index_RealToTime = db.Column(db.DateTime)
    Index_ShipMode = db.Column(db.Integer)
    Index_CreateTime = db.Column(db.DateTime)
    Index_ToContact = db.Column(db.String(128))
    Index_CreatorCompanyID = db.Column(db.Integer)


class SmsSendtrack(db.Model):
    __tablename__ = 'Sms_Send_Track'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    ID = db.Column(db.BigInteger, nullable=False, index=True, primary_key=True)
    Index_Id = db.Column(db.BigInteger)
    Index_Code = db.Column(db.String(128))
    Index_PactCode = db.Column(db.String(128))
    Index_FromProvince = db.Column(db.Integer)
    Index_FromCity = db.Column(db.Integer)
    Index_FromDistrict = db.Column(db.Integer)
    Index_ToProvince = db.Column(db.Integer)
    Index_ToCity = db.Column(db.Integer)
    Index_ToDistrict = db.Column(db.Integer)
    Index_FromTime = db.Column(db.DateTime)
    Index_ToTime = db.Column(db.DateTime)
    Index_Status = db.Column(db.String(128))
    Index_Status_SMS = db.Column(db.String(128))
    Index_FromLocation = db.Column(db.String(128))
    Index_ToLocation = db.Column(db.String(128))
    Index_RootOrderID = db.Column(db.Integer)
    Index_Fromtype = db.Column(db.Integer)
    Index_Totype = db.Column(db.Integer)
    Index_StartMsgTime = db.Column(db.DateTime)
    Index_ArriveMsgTime = db.Column(db.DateTime)
    Index_StartMsgStatus = db.Column(db.Integer)
    Index_ArriveMsgStatus = db.Column(db.Integer)
    Index_EndStatus = db.Column(db.Integer)
    Index_SignTime = db.Column(db.DateTime)
    Index_DeviceCode = db.Column(db.String(512))
    Index_DeviceBindingTime = db.Column(db.DateTime)
    Index_RealToTime = db.Column(db.DateTime)
    Index_CreateTime = db.Column(db.DateTime)
    Index_NoStartMsgRes = db.Column(db.String(512), default='0')
    Index_NoArriveMsgRes = db.Column(db.String(512), default='0')
    Index_NoArriveRes = db.Column(db.String(512), default='0')
    Index_ShipMode = db.Column(db.Integer)
    Index_UpdateTime = db.Column(db.DateTime, default='1900-01-01 00:00:00.0000000')
    Index_ToContact = db.Column(db.String(512))
    Index_CreatorCompanyID = db.Column(db.Integer)
    Index_NoStartMsgCode = db.Column(db.Integer, default=0)
    Index_NoArriveMsgCode = db.Column(db.Integer, default=0)
    Index_NoArriveResCode = db.Column(db.Integer, default=0)


class ReceiptSetLog(db.Model):
    __tablename__ = 'Receipt_Set_Log'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IMEI = db.Column(db.String(255))
    IP = db.Column(db.String(128))
    Set_Name = db.Column(db.String(128))
    Content = db.Column(db.String(128))
    Set_Type = db.Column(db.String(128))
    Tag = db.Column(db.String(128))
    Status_Code = db.Column(db.String(128))
    Result = db.Column(db.String(128))
    Set_Time = db.Column(db.DateTime, default=datetime.now)
    User_ID = db.Column(db.Integer)
    CP_Name = db.Column(db.String(128))


class Salesarea(db.Model):
    __tablename__ = 'Sales_area'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    area_id = db.Column(db.Integer)
    area_name = db.Column(db.String(128))
    parent_id = db.Column(db.Integer)
    is_disable = db.Column(db.Integer, default=0)
    top_parent_id = db.Column(db.Integer, default=0)
    is_manager = db.Column(db.Integer, default=0)


class StockLog(db.Model):
    __tablename__ = 'Stock_Log'
    __bind_key__ = 'ere'
    __table_args__ = {'schema': 'ERE.dbo'}
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IMEI = db.Column(db.String(128))
    Creator_Name = db.Column(db.String(128))
    Insert_Time = db.Column(db.DateTime)
    Content = db.Column(db.String(255))
    Sales_Name = db.Column(db.String(128))


def get_location_time(t):
    t = t + +timedelta(hours=8)
    return t


def find_imei_info(imei):
    data = dict(Sales_name="", Company_Name="")
    TD = TMSDevice.query.filter_by(Device_IMEICode=imei)
    for i in TD:
        S_data = TMSSale.query.filter_by(Company_Id=i.Device_CompanyID)
        for k in S_data:
            data["Sales_name"] = k.Sales_name
            data["Company_Name"] = k.Company_Name
    db.session.close()
    return data


def get_all_imei(id=None):
    res = {
        "Sales_name": "",
        "Total": "",
        "Companys": "",
        'username': ''
    }
    company = {
        "Company_Name": "",
        "Total": "",
        "Company_Id": "",
        "IMEI": ""
    }
    dal1 = {
        'name': '市场一部',
        'datalist': ''
    }
    dal2 = {
        'name': '市场二部',
        'datalist': ''
    }
    dal3 = {
        'name': '市场三部',
        'datalist': ''
    }
    data = {}
    l1 = []
    l2 = []
    l3 = []
    p = Pinyin()
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        T = TMSSale.query.with_entities(TMSSale.Sales_Company).distinct().all()
        for Sales_Company in T:
            S_C = []
            N = TMSSale.query.filter(TMSSale.Sales_Company == Sales_Company[0], TMSSale.Is_disabled == 0,
                                     User.is_disable == 0, TMSSale.user_id == User.id).with_entities(
                TMSSale.user_id).distinct().all()  # 根据所属公司获得销售账号
            db.session.close()
            if Sales_Company[0] != '北京':
                for N_C in N:  # 遍历销售名字
                    m = []
                    C_N = TMSSale.query.filter(
                        and_(TMSSale.user_id == N_C.user_id, TMSSale.Is_disabled == 0)).all()  # 根据销售名字获得公司名字
                    db_data = db.session.query(User).filter(User.id == N_C.user_id, User.is_disable == 0).first()
                    res['Sales_name'] = db_data.sales_name
                    res['username'] = db_data.username
                    db.session.close()
                    for CN_N in C_N:
                        l = []
                        company["Company_Name"] = CN_N.Company_Name
                        query = db.session().query(TMSDevice.Device_IMEICode, TMSSale.Company_Name, TMSSale.Company_Id)
                        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                                 TMSSale.Company_Name == CN_N.Company_Name, TMSDevice.Device_Invalid == 0))
                        dat = query.all()
                        db.session.close()
                        for i in dat:
                            m_m = dict(Devices="")
                            company["Company_Id"] = i[2]
                            m_m["Devices"] = i[0]
                            l.append(m_m.copy())
                        company["IMEI"] = l
                        company["Total"] = len(l)
                        m.append(company.copy())
                        res['Companys'] = m
                        res['Total'] = len(m)
                    S_C.append(res.copy())
                dat = {p.get_initials(u"{}".format(Sales_Company[0]), u''): S_C}
                data = dict(data, **dat)
            else:
                for N_C in N:  # 遍历销售名字
                    m = []
                    C_N = TMSSale.query.filter(
                        and_(TMSSale.user_id == N_C.user_id, TMSSale.Is_disabled == 0)).all()  # 根据销售名字获得公司名字
                    db_data = db.session.query(User).filter(User.id == N_C.user_id, User.is_disable == 0).first()
                    res['Sales_name'] = db_data.sales_name
                    res['username'] = db_data.username
                    Pa_lv = TMSSale.query.filter(TMSSale.user_id == N_C.user_id).first()
                    db.session.close()
                    for CN_N in C_N:
                        l = []
                        company["Company_Name"] = CN_N.Company_Name
                        query = db.session().query(TMSDevice.Device_IMEICode, TMSSale.Company_Name, TMSSale.Company_Id)
                        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                                 TMSSale.Company_Name == CN_N.Company_Name, TMSDevice.Device_Invalid == 0))
                        dat = query.all()
                        db.session.close()
                        for i in dat:
                            m_m = dict(Devices="")
                            company["Company_Id"] = i[2]
                            m_m["Devices"] = i[0]
                            l.append(m_m.copy())
                        company["IMEI"] = l
                        company["Total"] = len(l)
                        m.append(company.copy())
                        res['Companys'] = m
                        res['Total'] = len(m)
                    if Pa_lv.Parent_level == '1':
                        l1.append(res.copy())
                    elif Pa_lv.Parent_level == '2':
                        l2.append(res.copy())
                    elif Pa_lv.Parent_level == '3':
                        l3.append(res.copy())
                dal1['datalist'] = l1
                dal2['datalist'] = l2
                dal3['datalist'] = l3
                dat = {'BJ': [dal1, dal2, dal3]}
            data = dict(data, **dat)
    else:
        T = TMSSale.query.with_entities(TMSSale.Sales_Company).distinct().filter(TMSSale.user_id == id,
                                                                                 TMSSale.Is_disabled == 0).all()
        db.session.close()
        for Sales_Company in T:
            S_C = []
            N = TMSSale.query.filter(TMSSale.Sales_Company == Sales_Company[0], TMSSale.Is_disabled == 0,
                                     TMSSale.user_id == id,
                                     User.is_disable == 0, TMSSale.user_id == User.id).with_entities(
                TMSSale.user_id).distinct().all()  # 根据所属公司获得销售账号
            db.session.close()
            if Sales_Company[0] != '北京':
                for N_C in N:  # 遍历销售名字
                    m = []
                    C_N = TMSSale.query.filter(
                        and_(TMSSale.user_id == N_C.user_id, TMSSale.Is_disabled == 0)).all()  # 根据销售名字获得公司名字
                    db_data = db.session.query(User).filter(User.id == N_C.user_id, User.is_disable == 0).first()
                    res['Sales_name'] = db_data.sales_name
                    res['username'] = db_data.username
                    db.session.close()
                    for CN_N in C_N:
                        l = []
                        company["Company_Name"] = CN_N.Company_Name
                        query = db.session().query(TMSDevice.Device_IMEICode, TMSSale.Company_Name, TMSSale.Company_Id)
                        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                                 TMSSale.Company_Name == CN_N.Company_Name, TMSDevice.Device_Invalid == 0,
                                 TMSSale.user_id == id))
                        dat = query.all()
                        db.session.close()
                        for i in dat:
                            m_m = dict(Devices="")
                            company["Company_Id"] = i[2]
                            m_m["Devices"] = i[0]
                            l.append(m_m.copy())
                        company["IMEI"] = l
                        company["Total"] = len(l)
                        m.append(company.copy())
                        res['Companys'] = m
                        res['Total'] = len(m)
                    S_C.append(res.copy())
                dat = {p.get_initials(u"{}".format(Sales_Company[0]), u''): S_C}
                data = dict(data, **dat)
            else:
                for N_C in N:  # 遍历销售名字
                    m = []
                    C_N = TMSSale.query.filter(
                        and_(TMSSale.user_id == N_C.user_id, TMSSale.Is_disabled == 0)).all()  # 根据销售名字获得公司名字
                    db_data = db.session.query(User).filter(User.id == N_C.user_id, User.is_disable == 0).first()
                    res['Sales_name'] = db_data.sales_name
                    res['username'] = db_data.username
                    Pa_lv = TMSSale.query.filter(TMSSale.Sales_name == C_N[0].Sales_name).first()
                    db.session.close()
                    for CN_N in C_N:
                        l = []
                        company["Company_Name"] = CN_N.Company_Name
                        query = db.session().query(TMSDevice.Device_IMEICode, TMSSale.Company_Name, TMSSale.Company_Id)
                        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                                 TMSSale.Company_Name == CN_N.Company_Name, TMSDevice.Device_Invalid == 0))
                        dat = query.all()
                        db.session.close()
                        for i in dat:
                            m_m = dict(Devices="")
                            company["Company_Id"] = i[2]
                            m_m["Devices"] = i[0]
                            l.append(m_m.copy())
                        company["IMEI"] = l
                        company["Total"] = len(l)
                        m.append(company.copy())
                        res['Companys'] = m
                        res['Total'] = len(m)
                    if Pa_lv.Parent_level == '1':
                        l1.append(res.copy())
                    elif Pa_lv.Parent_level == '2':
                        l2.append(res.copy())
                    elif Pa_lv.Parent_level == '3':
                        l3.append(res.copy())
                dal1['datalist'] = l1
                dal2['datalist'] = l2
                dal3['datalist'] = l3
                all_l = [dal1, dal2, dal3]
                all_data = [i for i in all_l if len(i['datalist']) != 0]
                dat = {'BJ': all_data}
                # if len(l1) == 0:
                #     dat = {'BJ': [dal2]}
                # elif len(l2) == 0:
                #     dat = {'BJ': [dal1]}
                # else:
                #     dat = {'BJ': [dal1, dal2]}
                data = dict(data, **dat)
    return data


# a = get_all_imei(id=23)
# print(a)


def get_expire_imei_list(page=1, size=20, tp=None, id=None):  # type =1 表示7天 0<a<=7  2表示60 7<a<=60 3表示过期 60<a
    dat = {
        'Device_IMEICode': '',
        'Device_InsertTime': '',
        'Device_Expiry_Endtime': '',
        'Sales_name': '',
        'Company_Name': '',
        'Company_ID': '',
        'Device_Status': '离线',

    }
    expire_c = 0
    expire7_c = 0
    expire60_c = 0
    b = datetime.now()
    query = db.session().query(TMSDevice, TMSSale)  # 多表联查
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2), TMSDevice.Device_Invalid == 0,
                 TMSSale.Is_disabled == 0))
        data = query.all()  # 获取全部数据
    else:
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2), TMSDevice.Device_Invalid == 0,
                 TMSSale.Is_disabled == 0,
                 TMSSale.user_id == id))
        data = query.all()  # 获取全部数据
    db.session.close()
    d = query.count()
    l = []
    if tp == 4:
        for i in data:
            if i.TMSDevice.Device_Expiry_Endtime != i.TMSDevice.Device_Expiry_Starttime and i.TMSDevice.Device_Expiry_Endtime != None:
                dat['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
                dat['Device_InsertTime'] = str(i.TMSDevice.Device_InsertTime.strftime("%Y-%m-%d %H:%M:%S"))
                dat['Device_Expiry_Endtime'] = str(i.TMSDevice.Device_Expiry_Endtime.strftime("%Y-%m-%d %H:%M:%S"))
                dat['Sales_name'] = i.TMSSale.Sales_name
                dat['Company_Name'] = i.TMSSale.Company_Name
                dat['Company_ID'] = i.TMSSale.Company_Id
                l.append(dat.copy())
    else:
        for i in data:
            if i.TMSDevice.Device_Expiry_Endtime != i.TMSDevice.Device_Expiry_Starttime and i.TMSDevice.Device_Expiry_Endtime != None:
                count = (i.TMSDevice.Device_Expiry_Endtime.date() - b.date()).days
                if tp == 1:
                    if 0 <= count <= 7:
                        # expire7_c = expire7_c + 1
                        dat['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
                        dat['Device_InsertTime'] = str(i.TMSDevice.Device_InsertTime.strftime("%Y-%m-%d %H:%M:%S"))
                        dat['Device_Expiry_Endtime'] = str(
                            i.TMSDevice.Device_Expiry_Endtime.strftime("%Y-%m-%d %H:%M:%S"))
                        dat['Sales_name'] = i.TMSSale.Sales_name
                        dat['Company_Name'] = i.TMSSale.Company_Name
                        dat['Company_ID'] = i.TMSSale.Company_Id
                        l.append(dat.copy())
                elif tp == 2:
                    if 7 < count <= 60:
                        # expire60_c = expire60_c + 1
                        dat['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
                        dat['Device_InsertTime'] = str(i.TMSDevice.Device_InsertTime.strftime("%Y-%m-%d %H:%M:%S"))
                        dat['Device_Expiry_Endtime'] = str(
                            i.TMSDevice.Device_Expiry_Endtime.strftime("%Y-%m-%d %H:%M:%S"))
                        dat['Sales_name'] = i.TMSSale.Sales_name
                        dat['Company_Name'] = i.TMSSale.Company_Name
                        dat['Company_ID'] = i.TMSSale.Company_Id
                        l.append(dat.copy())
                elif tp == 3:
                    if count < 0:
                        # expire_c = expire_c + 1
                        dat['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
                        dat['Device_InsertTime'] = str(i.TMSDevice.Device_InsertTime.strftime("%Y-%m-%d %H:%M:%S"))
                        dat['Device_Expiry_Endtime'] = str(
                            i.TMSDevice.Device_Expiry_Endtime.strftime("%Y-%m-%d %H:%M:%S"))
                        dat['Sales_name'] = i.TMSSale.Sales_name
                        dat['Company_Name'] = i.TMSSale.Company_Name
                        dat['Company_ID'] = i.TMSSale.Company_Id
                        l.append(dat.copy())
                else:
                    return 'key error,To be continued'
    start = (page - 1) * size
    end = size * page
    db.session.close()
    return l[start:end]


def query_data(Device_IMEICode='', Sales_name='', Company_Name='', **kwargs):
    query = db.session().query(TMSDevice, TMSSale)  # 多表联查
    query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
        and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
             TMSSale.Is_disabled == 0,
             TMSDevice.Device_IMEICode.like('{}%'.format(Device_IMEICode)),
             TMSDevice.Device_Invalid == 0,
             TMSSale.Sales_name.like("{}%".format(Sales_name)),
             TMSSale.Company_Name.like("{}%".format(Company_Name)))).order_by(TMSSale.Company_Name)
    dat = query.all()
    db.session.close()
    return dat


def query_data_page(page, size, Device_IMEICode='', Sales_name='', Company_Name='', id=None, type=None, username=None,
                    useraccount=None):
    expire_c = 0
    expire7_c = 0
    expire60_c = 0
    expire_c_list = []
    expire7_c_list = []
    expire60_c_list = []
    Lease_list = []
    Lease = 0
    query = db.session().query(TMSDevice, TMSSale)  # 多表联查
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSDevice.Device_IMEICode.like('%{}%'.format(Device_IMEICode)),
                 TMSDevice.Device_Invalid == 0,
                 TMSSale.Is_disabled == 0,
                 TMSSale.Sales_name.like("%{}%".format(Sales_name)),
                 TMSSale.Company_Name.like("%{}%".format(Company_Name)))).order_by(TMSSale.Company_Name)
        scount = query.count()
        all_data = query.all()
        query = query.paginate(int(page), int(size), False)
        dat = query.items
        count = db.session().query(TMSDevice, TMSSale).join(TMSSale,
                                                            TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSSale.Is_disabled == 0,
                 TMSDevice.Device_Invalid == 0))
        da = count.all()
        b = datetime.now()
        for i in da:
            if i.TMSDevice.Device_OwnerType == 1:
                Lease = Lease + 1
                Lease_list.append(i)
            if i.TMSDevice.Device_Expiry_Endtime != i.TMSDevice.Device_Expiry_Starttime and i.TMSDevice.Device_Expiry_Endtime is not None:
                ex_days = (i.TMSDevice.Device_Expiry_Endtime.date() - b.date()).days
                if 0 <= ex_days <= 7:
                    expire7_c = expire7_c + 1
                    expire7_c_list.append(i)
                elif 7 < ex_days <= 60:
                    expire60_c = expire60_c + 1
                    expire60_c_list.append(i)
                elif ex_days < 0:
                    expire_c = expire_c + 1
                    expire_c_list.append(i)
        count = count.count()
        db.session.close()
    else:
        id_list = get_all_id(id=id)
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSDevice.Device_IMEICode.like('%{}%'.format(Device_IMEICode)),
                 TMSDevice.Device_Invalid == 0,
                 TMSSale.user_id.in_(id_list),
                 TMSSale.Is_disabled == 0,
                 TMSSale.Sales_name.like("%{}%".format(Sales_name)),
                 TMSSale.Company_Name.like("%{}%".format(Company_Name)))).order_by(TMSSale.Company_Name)
        all_data = query.all()
        scount = query.count()
        query = query.paginate(int(page), int(size), False)
        dat = query.items
        count = db.session().query(TMSDevice, TMSSale).join(TMSSale,
                                                            TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSSale.Is_disabled == 0,
                 TMSDevice.Device_Invalid == 0, TMSSale.user_id.in_(id_list)))
        da = count.all()
        b = datetime.now()
        for i in da:
            if i.TMSDevice.Device_OwnerType == 1:
                Lease = Lease + 1
                Lease_list.append(i)
            if i.TMSDevice.Device_Expiry_Endtime != i.TMSDevice.Device_Expiry_Starttime and i.TMSDevice.Device_Expiry_Endtime is not None:
                ex_days = (i.TMSDevice.Device_Expiry_Endtime.date() - b.date()).days
                if 0 <= ex_days <= 7:
                    expire7_c = expire7_c + 1
                    expire7_c_list.append(i)
                elif 7 < ex_days <= 60:
                    expire60_c = expire60_c + 1
                    expire60_c_list.append(i)
                elif ex_days < 0:
                    expire_c = expire_c + 1
                    expire_c_list.append(i)
        count = count.count()
        db.session.close()
    return dat, count, expire7_c, expire60_c, expire_c, scount, Lease, expire7_c_list, expire60_c_list, expire_c_list, Lease_list, all_data


def search_imei_info(data):  # 公司名字，销售名字，设备名字
    res = {
        "Device_IMEICode": "",
        "Device_Expiry_Starttime": "",
        "Device_Expiry_Endtime": "",
        "Sales_name": "",
        "Company_Name": "",
        "Company_ID": "",
    }
    expire_c = 0
    expire7_c = 0
    expire60_c = 0
    res2 = {
        "Count": "",
        "datalist": ""
    }
    # l[(data['page']-1)*data['size']:data['size']*(data['page']-1)]
    l = []
    if data["type"] == 0:  # 表示在所有设备列表里查
        dat = query_data(**data)
        for i in dat:
            res["Device_IMEICode"] = i.TMSDevice.Device_IMEICode
            res["Device_Expiry_Starttime"] = str(i.TMSDevice.Device_Expiry_Starttime)
            res["Device_Expiry_Endtime"] = str(i.TMSDevice.Device_Expiry_Endtime)
            res["Sales_name"] = i.TMSSale.Sales_name
            res["Company_ID"] = i.TMSSale.Company_Id
            res["Company_Name"] = i.TMSSale.Company_Name
            l.append(res.copy())
        res2["Count"] = len(l)
        res2["datalist"] = l
    else:
        b = datetime.now()
        dat_1 = query_data(**data)
        for i in dat_1:
            if i.TMSDevice.Device_Expiry_Endtime != i.TMSDevice.Device_Expiry_Starttime and i.TMSDevice.Device_Expiry_Endtime != None:
                count = (i.TMSDevice.Device_Expiry_Endtime.date() - b.date()).days
                if data["type"] == 1:  # 7天内即将过期
                    if count > 0 <= 7:
                        # expire7_c = expire7_c + 1
                        res['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
                        res['Device_Expiry_Starttime'] = str(i.TMSDevice.Device_Expiry_Starttime)
                        res['Device_Expiry_Endtime'] = str(i.TMSDevice.Device_Expiry_Endtime)
                        res['Sales_name'] = i.TMSSale.Sales_name
                        res['Company_Name'] = i.TMSSale.Company_Name
                        res['Company_ID'] = i.TMSSale.Company_Id
                        l.append(res.copy())
                elif data["type"] == 2:  # 60天内即将过期
                    if count > 7 <= 60:
                        # expire60_c = expire60_c + 1
                        res['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
                        res['Device_Expiry_Starttime'] = str(i.TMSDevice.Device_Expiry_Starttime)
                        res['Device_Expiry_Endtime'] = str(i.TMSDevice.Device_Expiry_Endtime)
                        res['Sales_name'] = i.TMSSale.Sales_name
                        res['Company_Name'] = i.TMSSale.Company_Name
                        res['Company_ID'] = i.TMSSale.Company_Id
                        l.append(res.copy())
                elif data["type"] == 3:  # 已经过期
                    if count > 60:
                        # expire_c = expire_c + 1
                        res['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
                        res['Device_Expiry_Starttime'] = str(i.TMSDevice.Device_Expiry_Starttime)
                        res['Device_Expiry_Endtime'] = str(i.TMSDevice.Device_Expiry_Endtime)
                        res['Sales_name'] = i.TMSSale.Sales_name
                        res['Company_Name'] = i.TMSSale.Company_Name
                        res['Company_ID'] = i.TMSSale.Company_Id
                        l.append(res.copy())
                else:
                    return 'key error,To be continued'

    res2["Count"] = len(l)
    # res2["datalist"] = l
    # 分页
    res2["datalist"] = l[(data['page'] - 1) * data['size']:data['size'] * data['page'] - 1]
    return res2


def search_alarm_list(data):  # 设备异常表搜索
    res = {
        "Company_Name": "",
        "Company_ID": "",
        "Sales_name": "",
        "Device_IMEICode": "",
    }
    query = db.session().query(TMSDevice, TMSSale)  # 多表联查
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(TMSDevice.Device_IMEICode == data['imei'], or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSSale.Is_disabled == 0,
                 TMSDevice.Device_Invalid == 0)).order_by(TMSSale.Company_Name)
        dat = query.all()
        db.session.close()
    else:
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(TMSDevice.Device_IMEICode == data['imei'], or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSSale.Is_disabled == 0,
                 TMSDevice.Device_Invalid == 0, TMSSale.user_id == data['id'])).order_by(TMSSale.Company_Name)
        dat = query.all()
        db.session.close()
    for i in dat:
        res["Device_IMEICode"] = i.TMSDevice.Device_IMEICode
        res["Sales_name"] = i.TMSSale.Sales_name
        res["Company_ID"] = i.TMSSale.Company_Id
        res["Company_Name"] = i.TMSSale.Company_Name

    return res


def get_company_id_and_name(page, size):
    res = {
        "Company_Name": "",
        "Company_ID": "",
        "Sales_name": "",
        "Device_IMEICode": "",
    }
    l = []
    query = db.session().query(TMSDevice, TMSSale)  # 多表联查
    query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
        and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
             TMSSale.Is_disabled == 0,
             TMSDevice.Device_Invalid == 0)).order_by(TMSSale.Company_Name.desc()).paginate(int(page), int(size), False)
    dat = query.items
    db.session.close()
    for i in dat:
        res["Device_IMEICode"] = i.TMSDevice.Device_IMEICode
        res["Sales_name"] = i.TMSSale.Sales_name
        res["Company_ID"] = i.TMSSale.Company_Id
        res["Company_Name"] = i.TMSSale.Company_Name
        l.append(res.copy())
    return l


def get_all_company_id_and_name(id=None):
    res = {
        "Company_Name": "",
        "Company_ID": "",
        "Sales_name": "",
        "Device_IMEICode": "",
    }
    l = []
    query = db.session().query(TMSDevice, TMSSale)  # 多表联查
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(TMSDevice.Device_Type == 3, TMSDevice.Device_Invalid == 0, TMSSale.Is_disabled == 0)).order_by(
            TMSSale.Company_Name)
        dat = query.all()
        db.session.close()
    else:
        query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
            and_(TMSDevice.Device_Type == 3, TMSDevice.Device_Invalid == 0, TMSSale.Is_disabled == 0,
                 TMSSale.user_id == id)).order_by(TMSSale.Company_Name)
        dat = query.all()
        db.session.close()
    for i in dat:
        res["Device_IMEICode"] = i.TMSDevice.Device_IMEICode
        res["Sales_name"] = i.TMSSale.Sales_name
        res["Company_ID"] = i.TMSSale.Company_Id
        res["Company_Name"] = i.TMSSale.Company_Name
        l.append(res.copy())
    return l


def search_get_alarm_list(s_data, page, size, id):
    res = {
        "Company_Name": "",
        "Company_ID": "",
        "Sales_name": "",
        "Device_IMEICode": "",
    }
    # 将未传的字段赋值为空
    b_data = {
        'IMEI': '',
        "Sales_name": "",
        "Company_Name": "",
        "temperature": ''
    }
    s_data = {**b_data, **s_data}
    l = []
    query = db.session().query(TMSDevice, TMSSale)  # 多表联查

    s_data['IMEI'] = "%" + s_data['IMEI'] + "%"
    s_data['Sales_name'] = "%" + s_data['Sales_name'] + "%"
    s_data['Company_Name'] = "%" + s_data['Company_Name'] + "%"
    # s_data['temperature'] = "%" + str(s_data['temperature']) + "%"
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        if s_data['temperature'] == 0:
            Num = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(
                    TMSDevice.Device_Type.between(2, 3),
                    TMSDevice.Device_Invalid == 0,
                    TMSSale.Is_disabled == 0,
                    TMSSale.Sales_name.like(s_data['Sales_name']),
                    TMSSale.Company_Name.like(s_data['Company_Name']),
                    # TMSDevice.Device_temperature.like(s_data['temperature']),
                    TMSDevice.Device_IMEICode.like(s_data['IMEI']))).count()
            query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(
                    TMSDevice.Device_Type.between(2, 3),
                    TMSDevice.Device_Invalid == 0,
                    TMSSale.Sales_name.like(s_data['Sales_name']),
                    TMSSale.Company_Name.like(s_data['Company_Name']),
                    TMSSale.Is_disabled == 0,
                    # TMSDevice.Device_temperature.like(s_data['temperature']),
                    TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(TMSSale.Company_Name.desc()).paginate(
                int(page),
                int(size),
                False)
        else:
            Num = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(TMSDevice.Device_temperature == s_data['temperature'],
                     TMSDevice.Device_Type.between(2, 3),
                     TMSDevice.Device_Invalid == 0,
                     TMSSale.Is_disabled == 0,
                     TMSSale.Sales_name.like(s_data['Sales_name']),
                     TMSSale.Company_Name.like(s_data['Company_Name']),
                     # TMSDevice.Device_temperature.like(s_data['temperature']),
                     TMSDevice.Device_IMEICode.like(s_data['IMEI']))).count()
            query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(TMSDevice.Device_temperature == s_data['temperature'],
                     TMSDevice.Device_Type.between(2, 3),
                     TMSDevice.Device_Invalid == 0,
                     TMSSale.Sales_name.like(s_data['Sales_name']),
                     TMSSale.Company_Name.like(s_data['Company_Name']),
                     TMSSale.Is_disabled == 0,
                     # TMSDevice.Device_temperature.like(s_data['temperature']),
                     TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(TMSSale.Company_Name.desc()).paginate(
                int(page),
                int(size),
                False)
        dat = query.items
        db.session.close()
        for i in dat:
            res["Device_IMEICode"] = i.TMSDevice.Device_IMEICode
            res["Sales_name"] = i.TMSSale.Sales_name
            res["Company_ID"] = i.TMSSale.Company_Id
            res["Company_Name"] = i.TMSSale.Company_Name
            l.append(res.copy())

    else:
        my_id = get_all_id(id)
        if s_data['temperature'] == 0:
            Num = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(
                    TMSDevice.Device_Type.between(2, 3),
                    TMSDevice.Device_Invalid == 0,
                    TMSSale.Sales_name.like(s_data['Sales_name']),
                    TMSSale.Company_Name.like(s_data['Company_Name']),
                    # TMSDevice.Device_temperature == s_data['temperature'],
                    TMSSale.user_id.in_(my_id),
                    TMSSale.Is_disabled == 0,
                    TMSDevice.Device_IMEICode.like(s_data['IMEI']))).count()
            query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(
                    TMSDevice.Device_Type.between(2, 3),
                    TMSDevice.Device_Invalid == 0,
                    TMSSale.Sales_name.like(s_data['Sales_name']),
                    TMSSale.Company_Name.like(s_data['Company_Name']),
                    # TMSDevice.Device_temperature == s_data['temperature'],
                    TMSSale.user_id.in_(my_id),
                    TMSSale.Is_disabled == 0,
                    TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(TMSSale.Company_Name.desc()).paginate(
                int(page),
                int(size),
                False)
        else:
            Num = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(TMSDevice.Device_temperature == s_data['temperature'],
                     TMSDevice.Device_Type.between(2, 3),
                     TMSDevice.Device_Invalid == 0,
                     TMSSale.Sales_name.like(s_data['Sales_name']),
                     TMSSale.Company_Name.like(s_data['Company_Name']),
                     # TMSDevice.Device_temperature == s_data['temperature'],
                     TMSSale.user_id.in_(my_id),
                     TMSSale.Is_disabled == 0,
                     TMSDevice.Device_IMEICode.like(s_data['IMEI']))).count()
            query = query.join(TMSSale, TMSSale.Company_Id == TMSDevice.Device_CompanyID).filter(
                and_(TMSDevice.Device_temperature == s_data['temperature'],
                     TMSDevice.Device_Type.between(2, 3),
                     TMSDevice.Device_Invalid == 0,
                     TMSSale.Sales_name.like(s_data['Sales_name']),
                     TMSSale.Company_Name.like(s_data['Company_Name']),
                     # TMSDevice.Device_temperature == s_data['temperature'],
                     TMSSale.user_id.in_(my_id),
                     TMSSale.Is_disabled == 0,
                     TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(TMSSale.Company_Name.desc()).paginate(
                int(page),
                int(size),
                False)
        dat = query.items
        db.session.close()
        for i in dat:
            res["Device_IMEICode"] = i.TMSDevice.Device_IMEICode
            res["Sales_name"] = i.TMSSale.Sales_name
            res["Company_ID"] = i.TMSSale.Company_Id
            res["Company_Name"] = i.TMSSale.Company_Name
            l.append(res.copy())
    return l, Num


def search_pactcode_by_imei(s_data, page, size, id=None):
    b_data = {
        'IMEI': '',
        'PactCode': '',
        'Company_Name': '',
    }
    s_data = {**b_data, **s_data}
    p_data = {
        'Index_PactCode': '',
        'Index_FromTime': '',
        'Index_ToTime': '',
        'Company_Name': '',
        'Company_ID': '',
        'Index_Code': '',
        'Order_Status': ''
    }
    l = []
    da = {
        "count": '',
        "datalist": ''
    }
    s_data['IMEI'] = "%" + s_data['IMEI'] + "%"
    s_data['PactCode'] = "%" + s_data['PactCode'] + "%"
    s_data['Company_Name'] = "%" + s_data['Company_Name'] + "%"
    a = db.session().query(User).filter(User.id == id).first()
    if a.role_id:
        post_data = db.session.query(TMSOrderIndex.Index_PactCode,
                                     TMSOrderIndex.Index_FromTime,
                                     TMSOrderIndex.Index_ToTime,
                                     TMSSale.Company_Name,
                                     TMSDevice.Device_IMEICode,
                                     TMSSale.Company_Id,
                                     TMSOrderIndex.Index_Code,
                                     TMSOrderIndex.Index_Status,
                                     ).join(TMSDevice, TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex,
            TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode).filter(
            and_(TMSDevice.Device_Type.between(2, 3),
                 # TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 # TMSOrderIndex.Index_CreatorCompanyID == TMSSale.Company_Id,
                 TMSOrderIndex.Index_Status.between(2, 16),
                 TMSSale.Is_disabled == 0,
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(
            TMSOrderIndex.Index_FromTime.desc()).paginate(
            int(page), int(size), False)
        res = post_data.items
        for i in res:
            p_data['Index_PactCode'] = i[0]
            p_data['Index_FromTime'] = str(i[1].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Index_ToTime'] = str(i[2].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Company_Name'] = i[3]
            p_data['Index_DeviceCode'] = i[4]
            p_data['Company_ID'] = i[5]
            p_data['Index_Code'] = i[6]
            p_data['Order_Status'] = i[7]
            l.append(p_data.copy())

        count = db.session.query(TMSOrderIndex, TMSSale, TMSDevice).join(TMSDevice,
                                                                         TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex, TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode).filter(
            and_(TMSDevice.Device_Type.between(2, 3),
                 # TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 TMSOrderIndex.Index_Status.between(2, 16),
                 TMSSale.Is_disabled == 0,
                 # TMSOrderIndex.Index_CreatorCompanyID == TMSSale.Company_Id,
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).count()

        da["count"] = count
        da["datalist"] = l
        db.session.close()
    else:
        my_id = get_all_id(id)
        post_data = db.session.query(TMSOrderIndex.Index_PactCode,
                                     TMSOrderIndex.Index_FromTime,
                                     TMSOrderIndex.Index_ToTime,
                                     TMSSale.Company_Name,
                                     TMSDevice.Device_IMEICode,
                                     TMSSale.Company_Id,
                                     TMSOrderIndex.Index_Code,
                                     TMSOrderIndex.Index_Status,
                                     ).join(TMSDevice, TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex,
            TMSDevice.Device_CompanyID == TMSOrderIndex.Index_CreatorCompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 TMSOrderIndex.Index_CreatorCompanyID == TMSSale.Company_Id,
                 TMSOrderIndex.Index_Status.between(2, 32),
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSSale.user_id.in_(my_id),
                 TMSSale.Is_disabled == 0,
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).order_by(
            TMSOrderIndex.Index_FromTime.desc()).paginate(
            int(page), int(size), False)
        res = post_data.items
        for i in res:
            p_data['Index_PactCode'] = i[0]
            p_data['Index_FromTime'] = str(i[1].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Index_ToTime'] = str(i[2].strftime("%Y-%m-%d %H:%M:%S"))
            p_data['Company_Name'] = i[3]
            p_data['Index_DeviceCode'] = i[4]
            p_data['Company_ID'] = i[5]
            p_data['Index_Code'] = i[6]
            p_data['Order_Status'] = i[7]
            l.append(p_data.copy())

        count = db.session.query(TMSOrderIndex, TMSSale, TMSDevice).join(TMSDevice,
                                                                         TMSSale.Company_Id == TMSDevice.Device_CompanyID).join(
            TMSOrderIndex, TMSDevice.Device_CompanyID == TMSOrderIndex.Index_CreatorCompanyID).filter(
            and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                 TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
                 TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                 TMSOrderIndex.Index_Status.between(2, 32),
                 TMSOrderIndex.Index_CreatorCompanyID == TMSSale.Company_Id,
                 TMSSale.user_id.in_(my_id),
                 TMSSale.Is_disabled == 0,
                 TMSOrderIndex.Index_PactCode.like(s_data['PactCode']),
                 TMSSale.Company_Name.like(s_data['Company_Name']),
                 TMSDevice.Device_IMEICode.like(s_data['IMEI']))).count()

        da["count"] = count
        da["datalist"] = l
        db.session.close()
    return da


def assignment_company(data, ip, b=None):
    Sales_Set_Log = SalesSetLog()
    username = str(data["username"])  # 销售名字
    Company_ClientCode = data["Company_ClientCode"]  # 公司名字
    Sales_Company = str(data["Sales_Company"])  # 销售区域
    Contacts = str(data["Contacts"])  # 公司联系人
    if 'Parent_level' in data.keys():
        Parent_level = str(data["Parent_level"])
    else:
        Parent_level = None
    user = User()
    sales = TMSSale()
    a = user.query.filter(User.username == username).first()  # 获取用户id
    if None == a:
        return {'res': "该用户不存在!", "code": -201}
    b = db.session.query(TMSCompany.Company_ID, TMSCompany.Company_Name).filter(
        TMSCompany.Company_ClientCode == Company_ClientCode, TMSCompany.Company_Status == 2).first()  # 公司表查询该公司是否存在
    if None == b:
        return {'res': "该公司不存在!", "code": -202}
    if Sales_Company not in ['北京', '上海', '直销']:
        return {'res': "该销售区域不存在!", "code": -203}
    cp_id = db.session.query(TMSCompany).filter(TMSCompany.Company_ClientCode == Company_ClientCode,
                                                TMSCompany.Company_Status == 2,
                                                TMSCompany.Company_Invalid == 0).first().Company_ID
    d = sales.query.filter(TMSSale.Company_Id == cp_id, TMSSale.Is_disabled == 0).first()
    if None != d:
        return {'res': "该公司已分配!", "code": -204}
    if Parent_level in ['1', '2', '3']:
        sales.Parent_level = Parent_level
    sales.Company_Name = b[1]
    sales.Sales_Company = Sales_Company
    sales.Contacts = Contacts
    sales.user_id = a.id
    sales.Is_disabled = 0
    sales.Sales_name = a.sales_name
    sales.Company_Id = b[0]
    sales.Bind_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Sales_Set_Log.Creator_Name = 'admin'
    Sales_Set_Log.Company_ID = b[0]
    Sales_Set_Log.Insert_Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Sales_Set_Log.IP = ip
    Sales_Set_Log.User_Name = username
    Sales_Set_Log.Content = '{}将{}(公司名)分配给了{},操作地所在IP为:{}。'.format(Sales_Set_Log.Creator_Name, sales.Company_Name,
                                                                   username, ip)
    try:
        db.session.add(Sales_Set_Log)
        db.session.add(sales)
        db.session.commit()
        db.session.close()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return {'res': "分配失败!", "code": -205}
    # 6.响应结果
    return {'res': "分配成功!", "code": 200}


l = []


def find_parent(id):
    a = db.session.query(Salesarea).filter(Salesarea.area_id == id).first()
    if a.parent_id > 0:
        l.append(a.parent_id)
        return find_parent(a.parent_id)
    else:
        l.append(id)
        return l


def assignment_company2(data, ip, b=None):
    print('assignment_company2', data)
    Sales_Set_Log = SalesSetLog()
    Sales_Company = str(data["Sales_Company"])  # 销售区域
    username = str(data["username"])  #
    salesaccount = str(data["salesaccount"])  # 销售账号
    if 'Company_ClientCode' in data.keys():
        Company_ClientCode = data["Company_ClientCode"]  # 公司名字
    else:
        Company_ClientCode = ''
    if 'Contacts' in data.keys():
        Contacts = str(data["Contacts"])  # 公司联系人
    else:
        Contacts = ''
    Sales_Company = data["Sales_Company"]  # 所属区域
    area_res = db.session.query(Salesarea).filter(Salesarea.area_name == Sales_Company).first()
    area_id = area_res.area_id
    user = User()
    sales = TMSSale()
    a = user.query.filter(User.username == salesaccount).first()  # 获取用户id
    if None == a:
        return {'res': "该用户不存在!", "code": -201}
    b = db.session.query(TMSCompany.Company_ID, TMSCompany.Company_Name).filter(
        TMSCompany.Company_ClientCode == Company_ClientCode, TMSCompany.Company_Status == 2).first()  # 公司表查询该公司是否存在
    if None == b:
        return {'res': "该公司不存在!", "code": -202}
    if not area_res:
        return {'res': "该销售区域不存在!", "code": -203}
    cp_id = db.session.query(TMSCompany).filter(TMSCompany.Company_ClientCode == Company_ClientCode,
                                                TMSCompany.Company_Status == 2,
                                                TMSCompany.Company_Invalid == 0).first()
    if not cp_id:
        return {'res': "该公司不存在!", "code": -202}
    else:
        cp_id = cp_id.Company_ID
    d = sales.query.filter(TMSSale.Company_Id == cp_id, TMSSale.Is_disabled == 0).first()
    if None != d:
        return {'res': "该公司已分配!", "code": -204}
    if 'is_manager' in data.keys():
        a.is_manager = data['is_manager']
    p_list = find_parent(area_id)
    p_min = min(p_list)
    a.parent_id = area_id
    a.top_parent_id = p_min
    sales.Company_Name = b[1]
    sales.Sales_Company = Sales_Company
    sales.Contacts = Contacts
    sales.user_id = a.id
    sales.Is_disabled = 0
    sales.Sales_name = a.sales_name
    sales.Company_Id = b[0]
    sales.Bind_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Sales_Set_Log.Creator_Name = 'admin'
    Sales_Set_Log.Company_ID = b[0]
    Sales_Set_Log.Insert_Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Sales_Set_Log.IP = ip
    Sales_Set_Log.User_Name = salesaccount
    Sales_Set_Log.Content = '{}将{}(公司名)分配给了{},操作地所在IP为:{}。'.format(Sales_Set_Log.Creator_Name, sales.Company_Name,
                                                                   salesaccount, ip)
    try:
        db.session.add(Sales_Set_Log)
        db.session.add(sales)
        db.session.commit()
        db.session.close()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return {'res': "分配失败!", "code": -205}
    # 6.响应结果
    return {'res': "分配成功!", "code": 200}


def get_sales_list(page, size):
    # data = db.session.query(User, TMSSale).outerjoin(User, User.id == TMSSale.user_id).filter(
    #     User.username != 'admin').order_by(User.join_time).paginate(
    #     int(page), int(size), False)
    data = db.session.query(User).filter(
        User.username != 'admin').order_by(User.join_time).paginate(
        int(page), int(size), False)
    db.session.close()
    res = data.items
    data = {
        "user_id": '',
        "username": '',
        'Sales_name': '',
        'Sales_Company': '',
        'creat_time': '',
        'disable': '',
        'last_login_time': '',
        'Bind_Company': ''
    }
    r = {
        "count": '',
        "datalist": ''
    }
    l = []
    for i in res:
        m = []
        s_c = search_company_list(i.id, page, size)
        m.append(s_c)
        data['Bind_Company'] = m
        data['user_id'] = i.id
        data['username'] = i.username
        data['Sales_name'] = i.sales_name
        data['creat_time'] = i.join_time.split('.')[0]
        data['disable'] = i.is_disable
        data['last_login_time'] = i.last_seen.split('.')[0]
        d2 = db.session.query(TMSSale).filter(
            and_(TMSSale.user_id == i.id, TMSSale.Is_disabled == 0)).first()
        if d2:
            data['Sales_Company'] = d2.Sales_Company
        else:
            data['Sales_Company'] = ''
        l.append(data.copy())
    count = db.session.query(User).filter(
        User.username != 'admin').count()
    db.session.close()
    r['count'] = count
    r['datalist'] = l
    return r


def search_company_list(args, page, size):
    dat = {
        "Company_name": '',
        "Bind_time": '',
    }
    count = db.session.query(TMSSale).filter(
        TMSSale.user_id == args).count()
    if count > 0:
        data = db.session.query(TMSSale).filter(
            and_(TMSSale.user_id == args, TMSSale.Is_disabled == 0)).order_by(TMSSale.Bind_time) \
            # .paginate(int(page), int(size), False)
        res = data.all()
        l = []
        for i in res:
            dat['Company_name'] = i.Company_Name
            dat['Bind_time'] = str(i.Bind_time).split('.')[0]
            l.append(dat.copy())
        rd = {"count": count, 'datalist': l}
    else:
        rd = {"count": 0, 'datalist': 0}
    db.session.close()
    return rd


def set_account_properties(args):
    user_id = args["user_id"]
    type = args["type"]
    user = User()
    data = db.session.query(User).filter(
        User.id == user_id).first()
    # db.session.close()
    if type == 1:
        password = args["password"]
        if len(password) == 0:
            return '参数不能都为空'
        else:
            data.password_hash = generate_password_hash(password)
        try:
            db.session.commit()
            db.session.close()
        except Exception as e:
            current_app.logger.debug(e)
            db.session.rollback()
            return '修改失败！'
            # 6.响应结果
        db.session.close()
        return '修改成功'
    if type == 2:
        is_disable = args["is_disable"]
        if is_disable not in [0, 1]:
            return '参数错误'
        else:
            is_disable = is_disable

        data.is_disable = is_disable
        rs1 = db.session.query(TMSSale).filter(TMSSale.user_id == user_id, TMSSale.Is_disabled == 0).all()
        for k in rs1:
            k.Is_disabled = is_disable
        try:
            db.session.commit()
            db.session.close()
        except Exception as e:
            current_app.logger.debug(e)
            db.session.rollback()
            return '修改失败！'
            # 6.响应结果
        db.session.close()
        return '修改成功'


def get_devices_statues(q_data):
    b = datetime.now()
    l = []
    dat = {
        'Device_IMEICode': '',
        'Device_InsertTime': '',
        'Device_Expiry_Endtime': '',
        'Sales_name': '',
        'Company_Name': '',
        'Company_ID': '',
        'Device_Status': '',
        'lithium': '',
        'Device_OwnerType': ''
    }
    for i in q_data:
        dat['Device_InsertTime'] = i.TMSDevice.Device_InsertTime.strftime("%Y-%m-%d %H:%M:%S")
        if str(i.TMSDevice.Device_Expiry_Endtime) in ['None', '1900-01-01 00:00:00']:
            dat['Device_Expiry_Endtime'] = ' '
        if i.TMSDevice.Device_Expiry_Endtime != i.TMSDevice.Device_Expiry_Starttime and i.TMSDevice.Device_Expiry_Endtime is not None:
            ex_days = (i.TMSDevice.Device_Expiry_Endtime.date() - b.date()).days
            dat['Device_Expiry_Endtime'] = i.TMSDevice.Device_Expiry_Endtime.strftime("%Y-%m-%d %H:%M:%S")
        if i.TMSDevice.Device_IMEICode[8] == '6':
            st = Models.Status.objects(devId=str(i.TMSDevice.Device_IMEICode)).order_by('-devId').limit(1)
            dat['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
            dat['Sales_name'] = i.TMSSale.Sales_name
            dat['Company_Name'] = i.TMSSale.Company_Name
            dat['Company_ID'] = i.TMSSale.Company_Id
            dat['Device_OwnerType'] = i.TMSDevice.Device_OwnerType
            if len(st) != 0:
                for j in st:
                    dat['lithium'] = j.lithium
                    if (b - get_location_time(j.date)).total_seconds() > 420:
                        d = Models.SleepNotice.objects(imei=str(j.devId)).limit(1)
                        for m in d:
                            if m.date > j.date:
                                dat['Device_Status'] = '休眠'
                            else:
                                dat['Device_Status'] = '离线'
                    else:
                        dat['Device_Status'] = '在线'
            else:
                dat['Device_Status'] = '离线'
                dat['lithium'] = 0

            l.append(dat.copy())
            dat.clear()
        if i.TMSDevice.Device_IMEICode[8] == '7':
            st = Models.Log.objects(imei=str(i.TMSDevice.Device_IMEICode)).limit(1)
            dat['Device_IMEICode'] = i.TMSDevice.Device_IMEICode
            dat['Sales_name'] = i.TMSSale.Sales_name
            dat['Company_Name'] = i.TMSSale.Company_Name
            dat['Company_ID'] = i.TMSSale.Company_Id
            dat['Device_OwnerType'] = i.TMSDevice.Device_OwnerType
            if len(st) != 0:
                for j in st:
                    dat['lithium'] = str(j['content']).split(',')[-1]
                    if (b - get_location_time(j["time"])).total_seconds() < 420:
                        dat['Device_Status'] = '在线'
                    else:
                        dat['Device_Status'] = '离线'
            else:
                dat['Device_Status'] = '离线'
                dat['lithium'] = 0
            l.append(dat.copy())
            dat.clear()
    return l


def search_imei_info2(data={}):  # 公司名字，销售名字，设备名字
    expire_c = 0
    expire7_c = 0
    expire60_c = 0
    page = data['page']
    size = data['size']
    print(data)
    q_data, count, expire7_c, expire60_c, expire_c, scount, Lease, expire7_c_list, expire60_c_list, expire_c_list, Lease_list, all_data = query_data_page(
        **data)
    if data['type'] == 0:
        res = {
            'total': '',
            'Lease': '',
            'datalist': '',
            'Seven': '',  # 7天过期
            'Sixty': '',  # 60天过期
            'expire': '',  # 已过期 Device_InsertTime
            'seach_total': ''
        }
        l = get_devices_statues(q_data=q_data)
        res['datalist'] = l
        res["expire"] = expire_c
        res["Seven"] = expire7_c
        res["Sixty"] = expire60_c
        res["Lease"] = Lease
        if data.__contains__('Sales_name') or data.__contains__('Company_Name') or data.__contains__('Device_IMEICode'):
            res['total'] = count
            res['seach_total'] = scount
        else:
            res['total'] = count
    elif data['type'] == 1:
        if data.__contains__('Sales_name') or data.__contains__('Company_Name') or data.__contains__('Device_IMEICode'):
            l = get_devices_statues(q_data=list(set(expire7_c_list).intersection(set(all_data))))  # 取出所有数据和过期数据的交集
            start = (page - 1) * size
            end = size * page
            res = {'datalist': l[start:end], "total": expire7_c, 'seach_total': len(l)}
        else:
            l = get_devices_statues(q_data=expire7_c_list)
            start = (page - 1) * size
            end = size * page
            res = {'datalist': l[start:end], "Seven": expire7_c}
    elif data['type'] == 2:
        if data.__contains__('Sales_name') or data.__contains__('Company_Name') or data.__contains__('Device_IMEICode'):
            l = get_devices_statues(q_data=list(set(all_data).intersection(set(expire60_c_list))))
            start = (page - 1) * size
            end = size * page
            res = {'datalist': l[start:end], "total": expire60_c, 'seach_total': len(l)}
        else:
            l = get_devices_statues(q_data=expire60_c_list)
            start = (page - 1) * size
            end = size * page
            l[start:end]
            res = {'datalist': l[start:end], "Sixty": expire60_c}
    elif data['type'] == 3:
        if data.__contains__('Sales_name') or data.__contains__('Company_Name') or data.__contains__('Device_IMEICode'):
            l = get_devices_statues(q_data=list(set(all_data).intersection(set(expire_c_list))))
            start = (page - 1) * size
            end = size * page
            res = {'datalist': l[start:end], "total": expire_c, 'seach_total': len(l)}
        else:
            l = get_devices_statues(q_data=expire_c_list)
            start = (page - 1) * size
            end = size * page
            res = {'datalist': l[start:end], "expire": expire_c}
    elif data['type'] == 4:
        if data.__contains__('Sales_name') or data.__contains__('Company_Name') or data.__contains__('Device_IMEICode'):
            l = get_devices_statues(q_data=list(set(all_data).intersection(set(Lease_list))))
            start = (page - 1) * size
            end = size * page
            res = {'datalist': l[start:end], "total": Lease, 'seach_total': len(l)}
        else:
            l = get_devices_statues(Lease_list)
            start = (page - 1) * size
            end = size * page
            res = {'datalist': l[start:end], "Lease": Lease}
    return res


def get_root_id(Index_DeviceCode=None, Index_PactCode=None):
    root_id = db.session.query(TMSOrderIndex.Index_ID).filter(
        and_(TMSOrderIndex.Index_PactCode == Index_PactCode, TMSOrderIndex.Index_DeviceCode == Index_DeviceCode,
             TMSOrderIndex.Index_SrcOrderID == 0)).order_by(TMSOrderIndex.Index_CreateTime).all()
    db.session.close()
    l = []
    for i in root_id:
        l.append(i[0])
    return l


def search_sales_info(s_data):
    """

    @param s_data:
    @param size:
    @param page:

    """
    # 将未传的字段赋值为空
    b_data = {
        "Sales_name": "",
        "Company_Name": "",
    }
    s_data = {**b_data, **s_data}
    l = []
    s_data['Sales_name'] = "%" + s_data['Sales_name'] + "%"
    s_data['Company_Name'] = "%" + s_data['Company_Name'] + "%"
    page = s_data["page"]
    size = s_data["size"]
    res = db.session.query(User).filter(
        and_(User.username != 'admin', User.sales_name.like(s_data['Sales_name']))).order_by(User.join_time)
    db.session.close()
    res = res.all()
    r = {
        "count": '',
        "datalist": ''
    }
    Bind_Company = {
        "count": '',
        "datalist": ''
    }
    l = []
    for i in res:
        data = {
            "user_id": '',
            "username": '',
            'Sales_name': '',
            'Sales_Company': '',
            'creat_time': '',
            'disable': '',
            'last_login_time': '',
            'Bind_Company': ''
        }
        T_sales = db.session.query(TMSSale).filter(
            and_(TMSSale.user_id == i.id, TMSSale.Is_disabled == 0, TMSSale.Sales_Company.like(s_data['Company_Name'])))
        T_sales = T_sales.all()
        db.session.close()
        if len(T_sales) != 0:
            data["user_id"] = i.id
            data["username"] = i.username
            data["Sales_name"] = i.sales_name
            data["disable"] = i.is_disable
            data["creat_time"] = str(i.join_time).split('.')[0]
            data["last_login_time"] = str(i.last_seen).split('.')[0]
            m = []
            m_m = []
            BC = {"Company_name": '', "Bind_time": ''}
            for k in T_sales:
                data["Sales_Company"] = k.Sales_Company
                BC["Company_name"] = k.Company_Name
                BC["Bind_time"] = str(k.Bind_time).split('.')[0]
                m.append(BC.copy())
            Bind_Company["datalist"] = m
            Bind_Company["count"] = len(m)
            m_m.append(Bind_Company)
            data["Bind_Company"] = m_m
    return data


def get_no_company_sales():
    data = {
        "user_id": '',
        "username": '',
        'Sales_name': '',
        'Sales_Company': '',
        'creat_time': '',
        'disable': '',
        'last_login_time': '',
        'Bind_Company': []
    }
    r = {
        "count": '',
        "datalist": ''
    }
    dat = db.session.query(User).filter(User.username != 'admin', User.is_disable == 0).order_by(User.join_time).all()
    l = []
    for i in dat:
        d = db.session.query(TMSSale).filter(TMSSale.user_id ==i.id,TMSSale.Is_disabled == 0).first()
        if d is None:
            data["user_id"] = i.id
            data["username"] = i.username
            data["Sales_name"] = i.sales_name
            data["creat_time"] = str(i.join_time).split('.')[0]
            data["disable"] = i.is_disable
            data["last_login_time"] = str(i.last_seen).split('.')[0]
            l.append(data.copy())
    r["count"] = len(l)
    r["datalist"] = l
    return r

# print(get_no_company_sales())
def get_sales_list2(s_data):
    # 将未传的字段赋值为空  Parent_level
    b_data = {
        "username": "",
        "Company_Name": "",
        "user_name": "",
    }
    s_data = {**b_data, **s_data}
    l = []
    s_data['Company_Name'] = "%" + s_data['Company_Name'] + "%"
    if len(s_data['user_name']) != 0:
        dat = db.session.query(User).filter(
            and_(User.username != 'admin', User.username == s_data['user_name'], User.is_disable == 0)).order_by(
            User.join_time)
    else:
        s_data['user_name'] = "%" + s_data['user_name'] + "%"
        dat = db.session.query(User).filter(
            and_(User.username != 'admin', User.username.like(s_data['user_name']), User.is_disable == 0)).order_by(
            User.join_time)
    page = s_data["page"]
    size = s_data["size"]
    db.session.close()
    res = dat.all()
    data = {
        "user_id": '',
        "username": '',
        'Sales_name': '',
        'Sales_Company': '',
        'creat_time': '',
        'disable': '',
        'last_login_time': '',
        'Bind_Company': ''
    }
    r = {
        "count": '',
        "datalist": '',
        "no_company": ''
    }
    no_cp = get_no_company_sales()
    r["no_company"] = no_cp
    l = []
    for i in res:
        m = []
        s_c = search_company_list2(i.id, s_data['Company_Name'], page, size)
        if s_c['count'] != 0:
            m.append(s_c)
            data['Bind_Company'] = m
            data['user_id'] = i.id
            data['username'] = i.username
            data['Sales_name'] = i.sales_name
            data['creat_time'] = i.join_time.split('.')[0]
            data['disable'] = i.is_disable
            data['last_login_time'] = i.last_seen.split('.')[0]
            d2 = db.session.query(User).filter(User.id == i.id, User.is_disable == 0, User.role_id == 0).first()
            if d2.parent_id != 0:
                my_sales_compay = db.session.query(Salesarea).filter(Salesarea.area_id == d2.parent_id,
                                                                     Salesarea.is_disable == 0).first()
                data['Sales_Company'] = my_sales_compay.area_name
            else:
                data['Sales_Company'] = ''
            l.append(data.copy())
        db.session.close()
        page = s_data["page"]
        size = s_data["size"]
        start = (page - 1) * size
        end = size * page
    if len(l) > 0:
        r['count'] = len(l)
        r['datalist'] = l[start:end]
    else:
        r['datalist'] = []
    return r


def search_company_list2(args, Company_Name, page, size):
    dat = {
        "Company_name": '',
        "Bind_time": '',
        'Company_ID': '',
        'Contacts': ''
    }
    count = db.session.query(TMSSale).filter(and_(TMSSale.Is_disabled == 0,
                                                  TMSSale.user_id == args,
                                                  TMSSale.Is_disabled == 0,
                                                  TMSSale.Sales_Company.like(Company_Name))).count()
    if count > 0:
        data = db.session.query(TMSSale).filter(
            TMSSale.Is_disabled == 0, TMSSale.user_id == args, TMSSale.Sales_Company.like(Company_Name)).order_by(
            TMSSale.Bind_time) \
            # .paginate(int(page), int(size), False)
        res = data.all()
        l = []
        for i in res:
            dat['Company_name'] = i.Company_Name
            dat['Bind_time'] = str(i.Bind_time).split('.')[0]
            dat['Company_ID'] = i.Company_Id
            dat['Is_disabled'] = i.Is_disabled
            dat['Contacts'] = i.Contacts
            l.append(dat.copy())
        rd = {"count": count, 'datalist': l}
    else:
        rd = {"count": 0, 'datalist': 0}
    db.session.close()
    return rd


def change_sales_company(Company_Id, user_name=None, disable=0):
    res1 = db.session.query(TMSSale).filter(TMSSale.Company_Id == Company_Id).first()
    user_id = res1.user_id
    username = db.session.query(User).filter(User.id == user_id).first().username
    res1.Is_disabled = disable
    if user_name is not None:
        user_id = db.session.query(User.id).filter(User.username == user_name).first()
        if user_id is None:
            return {'result': '无效的用户'}, username
        else:
            user_name2 = db.session.query(TMSSale).filter(TMSSale.user_id == user_id[0]).first()
            res1.user_id = user_id[0]
            res1.Sales_name = user_name2.Sales_name
    try:
        db.session.commit()
        db.session.close()
    except Exception as e:
        current_app.logger.debug(e)
        res1.db.session.rollback()
        return {'result': '修改失败'}, username
    return {'result': '修改成功'}, username


def get_sales_log(salesaccount, page, size):
    res = db.session.query(SalesSetLog).filter(
        or_(SalesSetLog.User_Name == salesaccount, SalesSetLog.Last_Sales == salesaccount)).order_by(
        SalesSetLog.Insert_Time.desc()).paginate(int(page), int(size), error_out=False)
    data = {
        'total_page': res.pages,
        'datalist': '',
        'total': res.total
    }
    datalist = []
    for i in res.items:
        dat_info = {'ip': i.IP, 'content': i.Content}
        datalist.append(dat_info)
    data['datalist'] = datalist
    return data


def renew_device(user_id, imei, end_time, ip, useraccount, username):  # 续费
    Sales_Set_Log = ReceiptLog()
    role = db.session.query(User).filter(User.id == user_id).first()
    Company_Id = db.session.query(TMSSale.Company_Id).filter(
        and_(TMSSale.Is_disabled == 0, TMSSale.user_id == user_id)).all()
    device = db.session.query(TMSDevice).filter(TMSDevice.Device_IMEICode == imei,
                                                TMSDevice.Device_Invalid == 0).first()
    try:
        end_time = datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S")
    except Exception:
        return {'result': '日期格式错误！'}
    l = []
    if role.role_id == 1:
        device.Device_Expiry_Endtime = end_time
        # sales_user_id = db.session.query(TMSSale).filter(TMSSale.Company_Id == device.Device_CompanyID).first().user_id
        Sales_Set_Log.User_Name = username
    else:
        Sales_Set_Log.User_Name = username
        for i in Company_Id:
            l.append(i[0])
        if int(i[0]) in l:
            device.Device_Expiry_Endtime = end_time
            Sales_Set_Log.User_Name = username
        else:
            return {'result': '该设备不属于该销售。'}
    Sales_Set_Log.Set_Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Sales_Set_Log.Creator_Name = useraccount
    Sales_Set_Log.Company_ID = device.Device_CompanyID
    Sales_Set_Log.IP = ip
    Sales_Set_Log.IMEI = imei
    Company_Name = db.session.query(TMSCompany).filter(
        TMSCompany.Company_ID == device.Device_CompanyID).first().Company_Name
    Sales_Set_Log.Content = '{}将{}(公司名)编号为{}的设备进行了续费，新的试用结束时间为{},操作地所在IP为:{}。'.format(Sales_Set_Log.Creator_Name,
                                                                                      Company_Name, imei, end_time, ip)
    try:
        db.session.add(Sales_Set_Log)
        db.session.commit()
        db.session.close()
    except Exception as e:
        print(e)
        current_app.logger.debug(e)
        db.session.rollback()
        return {'result': '修改失败。'}
    return {'result': '修改成功。'}


# 189
# a = renew_device(user_id=34, imei=351608086032534, end_time='2020-04-25 00:00:00', ip='192.168.1.52')
# print(a)

def get_start_end_time(day_now):
    day_now = time.strptime(day_now, '%Y-%m-%d')
    day_begin = '%d-%02d-01' % (day_now.tm_year, day_now.tm_mon)  # 月初肯定是1号
    wday, monthRange = calendar.monthrange(day_now.tm_year, day_now.tm_mon)  # 得到本月的天数 第一返回为月第一日为星期几（0-6）, 第二返回为此月天数
    day_end = '%d-%02d-%02d' % (day_now.tm_year, day_now.tm_mon, monthRange)
    return day_begin, day_end


def get_msg_count(user_id, day_now):  # 获取短信总数
    a = db.session.query(User).filter(User.id == user_id).first()
    l = []
    start = 0
    arrive = 0
    s_time, e_time = get_start_end_time(day_now)
    if a.role_id:
        user_id_list = db.session.query(User, TMSSale).filter(User.id == TMSSale.user_id).all()
        for c in user_id_list:
            l.append(c.TMSSale.Company_Id)
        start_count = db.session.query(TMSDevice, TMSOrderIndex).filter(and_(
            or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
            TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
            TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
            TMSOrderIndex.Index_StartMsgTime != '1900-01-01 00:00:00',
            TMSOrderIndex.Index_StartMsgTime.between(s_time, e_time),
            TMSDevice.Device_CompanyID.in_(l))).count()
        arrive_count = db.session.query(TMSDevice, TMSOrderIndex).filter(and_(
            or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
            TMSDevice.Device_IMEICode == TMSOrderIndex.Index_DeviceCode,
            TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
            TMSOrderIndex.Index_ArriveMsgTime != '1900-01-01 00:00:00',
            TMSOrderIndex.Index_ArriveMsgTime.between(s_time, e_time),
            TMSDevice.Device_CompanyID.in_(l))).count()
        start = start_count + start
        arrive = arrive_count + arrive
    else:
        u_id = get_all_id(user_id)
        Company_ID = db.session.query(TMSSale).filter(TMSSale.user_id.in_(u_id)).all()
        for i in Company_ID:
            imei = db.session.query(TMSDevice).filter(
                and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                     TMSDevice.Device_Invalid == 0,
                     TMSSale.Is_disabled == 0,
                     TMSDevice.Device_CompanyID == i.Company_Id)).all()
            for device_imei in imei:
                start_count = db.session.query(TMSOrderIndex).filter(
                    and_(TMSOrderIndex.Index_DeviceCode == device_imei.Device_IMEICode,
                         TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                         TMSOrderIndex.Index_StartMsgTime != '1900-01-01 00:00:00',
                         TMSOrderIndex.Index_StartMsgTime.between(s_time, e_time)
                         )).count()
                arrive_count = db.session.query(TMSOrderIndex).filter(
                    and_(TMSOrderIndex.Index_DeviceCode == device_imei.Device_IMEICode,
                         TMSOrderIndex.Index_ID == TMSOrderIndex.Index_RootOrderID,
                         TMSOrderIndex.Index_ArriveMsgTime != '1900-01-01 00:00:00',
                         TMSOrderIndex.Index_ArriveMsgTime.between(s_time, e_time)
                         )).count()
                start = start_count + start
                arrive = arrive_count + arrive
    return arrive + start


def get_parent_level(args):
    data = {
        "user_id": '',
        "username": '',
        'Sales_name': '',
        'Sales_Company': '',
        'creat_time': '',
        'disable': '',
        'last_login_time': '',
        'Bind_Company': ''
    }
    r = {
        "count": '',
        "datalist": '',
        "no_company": ''
    }
    no_cp = get_no_company_sales()
    r["no_company"] = no_cp
    dat = {
        "Company_name": '',
        "Bind_time": '',
        'Company_ID': '',
        'Contacts': ''
    }
    r2 = {
        "count": '',
        "datalist": ''
    }
    Parent_level = args['Parent_level']
    page = args['page']
    size = args['size']
    p_data = db.session.query(TMSSale, User).filter(
        and_(TMSSale.user_id == User.id, TMSSale.Parent_level == Parent_level, User.is_disable == 0)).paginate(
        int(page), int(size), False)
    r_data = p_data.items
    l = []
    u_id = []
    for i in r_data:
        k_l = []
        if i.TMSSale.user_id not in u_id:
            data['user_id'] = i.TMSSale.user_id
            data['username'] = i.User.username
            data['Sales_name'] = i.TMSSale.Sales_name
            data['Sales_Company'] = i.TMSSale.Sales_Company
            data['creat_time'] = i.User.join_time.split('.')[0]
            # print(i.User.join_time.split('.')[0])
            data['disable'] = i.User.is_disable
            data['last_login_time'] = i.User.last_seen.split('.')[0]
            u_id.append(i.TMSSale.user_id)
            c_data = db.session.query(TMSSale).filter(TMSSale.user_id == i.TMSSale.user_id).all()
            for k in c_data:
                dat["Company_name"] = k.Company_Name
                dat["Bind_time"] = k.Bind_time.split('.')[0]
                dat["Company_ID"] = k.Company_Id
                dat["Contacts"] = k.Contacts
                k_l.append(dat.copy())
            r2['datalist'] = k_l
            r2['count'] = len(k_l)
            data['Bind_Company'] = [r2]
            l.append(data.copy())
            r['datalist'] = l
            r['count'] = len(l)
    return r


def get_CustomerSymbolName(Index_Code):
    rs = db.session.query(TMSOrderIndex).filter(TMSOrderIndex.Index_Code == Index_Code,
                                                TMSOrderIndex.Index_RootOrderID == TMSOrderIndex.Index_ID).first()
    CustomerSymbolName = rs.Index_CustomerSymbolName
    return CustomerSymbolName

# data = {"role_id": 1, "page": 1, "size": 20, "Parent_level": 1, "id": "23"}
# a = get_parent_level(data)
# print(a)
