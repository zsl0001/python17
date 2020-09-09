import mongoengine
from sqlalchemy import create_engine, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
# --------------连接数据库需要的类---------------
from sqlalchemy import create_engine  # 建立数据库引擎
from sqlalchemy.orm import sessionmaker  # 建立会话session

Base = declarative_base()  # 实例,创建基类
# db_connect_string = 'mssql+pymssql://WLY:Wly2.techns@907@172.16.16.23:1433/ERE?charset=utf8'
db_connect_string = 'mssql+pymssql://WLY:Wly2.techns@907@192.168.1.200:1433/ERE?charset=utf8'
# 以mysql数据库为例：mysql+数据库驱动：//用户名：密码@localhost:3306/数据库
engine = create_engine(db_connect_string)  # 创建引擎
Sesssion = sessionmaker(bind=engine)  # 产生会话
session = Sesssion()  # 创建Session实例
con = mongoengine.connect(db='er', host='192.168.1.168')


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


class StartMessage(mongoengine.Document):
    meta = {
        'collection': 'startMessage',
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


class TMSOrderIndex(Base):
    __tablename__ = 'TMS_OrderIndex'
    __table_args__ = {'schema': 'WLY.dbo'}
    Index_ID = Column(BigInteger, primary_key=True)
    opt_status = Column(Integer, nullable=False, )
    Index_Code = Column(String(50), nullable=False)
    Index_PactCode = Column(String(50))
    Index_EndUserID = Column(BigInteger, )
    Index_EndUserName = Column(String(300))
    Index_From = Column(String(300))
    Index_FromProvince = Column(BigInteger, )
    Index_FromCity = Column(BigInteger, )
    Index_FromDistrict = Column(BigInteger, )
    Index_FromTime = Column(DateTime)
    Index_To = Column(String(300))
    Index_ToProvince = Column(BigInteger, )
    Index_ToCity = Column(BigInteger, )
    Index_ToDistrict = Column(BigInteger, )
    Index_ToTime = Column(DateTime)
    Index_TransportMode = Column(BigInteger)
    Index_GoodsCategory = Column(BigInteger)
    Index_PackageMode = Column(BigInteger)
    Index_ChargeMode = Column(BigInteger)
    Index_PriceUnit = Column(BigInteger)
    Index_Status = Column(BigInteger, nullable=False, )
    Index_StatusTime = Column(DateTime, nullable=False)
    Index_SrcOrderID = Column(BigInteger, index=True, )
    Index_RootOrderID = Column(BigInteger, index=True, )
    Index_SrcClass = Column(BigInteger, nullable=False, )
    Index_Kms = Column(BigInteger, )
    Index_CarType = Column(BigInteger, )
    Index_DriverID = Column(BigInteger, )
    Index_CarID = Column(BigInteger, )
    Index_SupplierID = Column(BigInteger, )
    Index_SupplierCompanyID = Column(BigInteger, )
    Index_CustomerID = Column(BigInteger, )
    Index_CustomerCompanyID = Column(BigInteger, )
    Index_ShipMode = Column(BigInteger, )
    Index_Pick = Column(BigInteger, )
    Index_Delivery = Column(BigInteger, )
    Index_Creator = Column(BigInteger, nullable=False, )
    Index_CreatorCompanyID = Column(BigInteger, nullable=False, )
    Index_CreateTime = Column(DateTime, nullable=False, )
    Index_Confirmer = Column(BigInteger, )
    Index_ConfirmTime = Column(DateTime)
    Index_Singer = Column(BigInteger, )
    Index_SignTime = Column(DateTime)
    Index_ReceiptDoc = Column(String(512))
    Index_Exception = Column(String(512), )
    Index_Invalid = Column(Integer, nullable=False, )
    Index_Comments = Column(String(256, 'Chinese_PRC_CI_AS'))
    Index_OnLoad = Column(BigInteger, )
    Index_OffLoad = Column(BigInteger, )
    Index_Insurance = Column(BigInteger, )
    Index_Description = Column(String, )
    Index_Combined = Column(BigInteger, )
    Index_CustomerSymbolID = Column(BigInteger, )
    Index_SupplierSymbolID = Column(BigInteger, )
    Index_ReceiptDoc1 = Column(String(512))
    Index_ReceiptDoc2 = Column(String(512))
    Index_ReceiptDoc3 = Column(String(512))
    Index_FromContact = Column(String(300))
    Index_ToContact = Column(String(300))
    Index_PrevOrderID = Column(BigInteger, )
    Index_DeviceCode = Column(String(50))
    Index_GoodsLst = Column(String)
    Index_RealFromTime = Column(DateTime)
    Index_RealToTime = Column(DateTime)
    Index_ReceiptDoc4 = Column(String(512))
    Index_ReceiptDoc5 = Column(String(512))
    Index_ReceiptDoc6 = Column(String(512))
    Index_ReceiptDoc7 = Column(String(512))
    Index_ReceiptDoc8 = Column(String(512))
    Index_ReceiptDoc9 = Column(String(512))
    Index_FromOperator = Column(String(100))
    Index_TerminalOrderID = Column(BigInteger, )
    Index_TerminalOrderCode = Column(String(100))
    Index_CustomerName = Column(String(300), )
    Index_SupplierName = Column(String(300), )
    Index_CreatorCompanyName = Column(String(300), )
    Index_CustomerSymbolName = Column(String(300), )
    Index_SupplierSymbolName = Column(String(300), )
    Index_BeSplit = Column(Integer, )
    Index_SplitType = Column(Integer, )
    Index_CombinedOrderAmount = Column(BigInteger, )
    Index_CombinedFrom = Column(String(300), )
    Index_CombinedTo = Column(String(300), )
    Index_TCacheReady = Column(Integer, )
    Index_StartMsgTime = Column(DateTime, )
    Index_ArriveMsgTime = Column(DateTime, )
    Index_VerifyCode = Column(String(6, 'Chinese_PRC_CI_AS'), )
    Index_DeviceCreatTime = Column(DateTime, )
    Index_GPSStartTime = Column(DateTime, )
    Index_DeviceBindingTime = Column(DateTime, )
    Index_FromLocation = Column(String(50, 'Chinese_PRC_CI_AS'), )
    Index_ToLocation = Column(String(50, 'Chinese_PRC_CI_AS'), )
    Index_ContainsBillDay = Column(DateTime, )
    Index_TrackType = Column(Integer, )
    Index_Fromtype = Column(Integer, nullable=False, )
    Index_Totype = Column(Integer, nullable=False, )
    Index_RollBack = Column(Integer, nullable=False, )
    Index_CusRollBack = Column(Integer, nullable=False, )
    Index_tpPrint = Column(String(200, 'Chinese_PRC_CI_AS'), )
    Index_GUID = Column(String(50), )
    Index_FromManID = Column(Integer)
    Index_FromMan = Column(String(50))
    Index_ToManID = Column(Integer)
    Index_ToMan = Column(String(50))
    Index_RollBackOrderID = Column(BigInteger, nullable=False, )
    Index_ReceipTime = Column(DateTime)
    Index_ExceptionType = Column(Integer, )
    Index_AssessLevel = Column(Integer, )
    Index_AssessMent = Column(String(200), )
    Index_CloseMark = Column(Integer, )
    Index_CloseMent = Column(String(100), )
    Index_Addorder = Column(Integer, nullable=False, )
    Index_AddPacth = Column(String(200), )
    Index_CarCount = Column(Integer, nullable=False, )
    Index_AutoSchedule = Column(Integer, nullable=False, )
    Index_CombinePrice = Column(Integer, nullable=False, )
    Index_OrderType = Column(Integer, )
    Index_SupplierType = Column(Integer, )
    Index_CloseInitiator = Column(String(100))
    Index_CloseType = Column(BigInteger)
    Index_signinfotype = Column(Integer, )
    Index_signinfo = Column(String)
    Index_RollBckLst = Column(String, )
    Index_VerifySiginTime = Column(DateTime, )
    Index_CreateType = Column(Integer, nullable=False, )
    Index_ReceiptType = Column(Integer)
    Index_additionTransportType = Column(String(1))
    Index_DeviceCode2 = Column(String(255))
    Index_RealFromStatus = Column(Integer)
    Index_WithChildType = Column(Integer)


class TMSCompany(Base):
    __tablename__ = 'TMS_Company'
    __table_args__ = {'schema': 'WLY.dbo'}
    Company_ID = Column(BigInteger, nullable=False, index=True, primary_key=True)
    Company_Name = Column(String(300))
    Company_Status = Column(BigInteger)
    Company_Invalid = Column(Integer)


class TMSDevice(Base):
    __tablename__ = 'TMS_Devices'
    __table_args__ = {'schema': 'WLY.dbo'}
    Device_ID = Column('Device_ID', BigInteger, nullable=False, index=True, primary_key=True)
    Device_IMEICode = Column('Device_IMEICode', nullable=False)
    Device_CompanyID = Column('Device_CompanyID', BigInteger)
    Device_Invalid = Column('Device_Invalid', Integer)
    Device_Type = Column('Device_Type', Integer, nullable=False)


def get_msg_info(Company_name=None, Index_PactCode=None, Index_Code=None, Order_Status=None, CustomerSymbolName=None):
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
        for k in sms_start:
            start_res_data["send_location"] = (k.lng, k.lat)
    for s2 in sms2:
        sms_end = ArriveMessage.objects(code=s2.code)
        for m in sms_end:
            arriv_res_data["send_location"] = (m.lng, m.lat)
    l = {'start': start_res_data, 'arr': arriv_res_data}
    con.disconnect
    return l


res = session.query(TMSCompany).filter(TMSCompany.Company_Name == '上海中保物流有限公司', TMSCompany.Company_Invalid == 0,
                                       TMSCompany.Company_Status == 2).first()
print(res.Company_ID)

res = session.query(TMSDevice).filter(TMSDevice.Device_CompanyID == res.Company_ID, TMSDevice.Device_Invalid == 0).all()
l = [i.Device_IMEICode for i in res]
# print(l)
res = session.query(TMSOrderIndex).filter(TMSOrderIndex.Index_RootOrderID == TMSOrderIndex.Index_ID,
                                          TMSOrderIndex.Index_DeviceCode.in_(l),
                                          TMSOrderIndex.Index_CreateTime.between('2019-12-12', '2020-12-12')).all()
for i in res:
    print(i.Index_CustomerSymbolName, i.Index_CreatorCompanyName, i.Index_PactCode, i.Index_DeviceCode)
    startswith = str(i.Index_CreatorCompanyName) + "|" + str(i.Index_PactCode)
    endwith = str(i.Index_PactCode) + "|" + str(i.Index_CreatorCompanyName)
    sms = SmsQueue.objects.filter(content__startswith=startswith)
    if len(sms) == 0:
        startswith = str(i.Index_CustomerSymbolName) + "|" + str(i.Index_PactCode)
        sms = SmsQueue.objects.filter(content__startswith=startswith)
        if len(sms) == 0:
            start_res_data = []
    sms2 = SmsQueue.objects.filter(content__startswith=endwith)
    if len(sms2) == 0:
        endwith = str(i.Index_PactCode) + "|" + str(i.Index_CustomerSymbolName)
        sms2 = SmsQueue.objects.filter(content__startswith=endwith)
        if len(sms2) == 0:
            arriv_res_data = []
    for s in sms:
        sms_start = StartMessage.objects(code=s.code)
        cont = s.content.split('|')
        start_res_data["sms_content"] = start_res_data["sms_content"].format(*cont)
        for k in sms_start:
            start_res_data["send_location"] = (k.lng, k.lat)
    for s2 in sms2:
        sms_end = ArriveMessage.objects(code=s2.code)
        cont = s2.content.split('|')
        arriv_res_data["sms_content"] = arriv_res_data["sms_content"].format(*cont)
        for m in sms_end:
            arriv_res_data["send_location"] = (m.lng, m.lat)
    l = [start_res_data, arriv_res_data]
    print(l)
    con.disconnect
