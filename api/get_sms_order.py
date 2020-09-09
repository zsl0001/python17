from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import currentThread

import sys
from math import radians, cos, sin, asin, sqrt
from concurrent.futures import ThreadPoolExecutor

sys.path.append("..")
from datetime import datetime, timedelta
from time import sleep

from sqlalchemy import or_, and_
from geopy.distance import geodesic
from models import *
from models import SmsSendtrack
from api.get_more_postion import More_Position
from my_db.Models import Position
from mongoengine.queryset.visitor import Q
import re

str_p = '2000-01-01 00:00:00'
d = datetime.strptime(str_p, '%Y-%m-%d %H:%M:%S')


def local2utc(local_st):
    """本地时间转UTC时间（-8: 00）"""
    local_st = datetime.strptime(local_st, '%Y-%m-%d %H:%M:%S')
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.utcfromtimestamp(time_struct)
    return utc_st


def get_sms_order():  # 同步SMS表所有的订单
    sms_track_Index_Id = db.session.query(SmsSendtrack.Index_Id).filter(
        SmsSendtrack.Index_Status_SMS.between(0, 16)).order_by(
        SmsSendtrack.Index_Id.desc()).first()
    sms_order_list = db.session.query(TMSOrderIndexSms.Index_Id,
                                      TMSOrderIndexSms.Index_Code,
                                      TMSOrderIndexSms.Index_PactCode,
                                      TMSOrderIndexSms.Index_FromProvince,
                                      TMSOrderIndexSms.Index_FromCity,
                                      TMSOrderIndexSms.Index_FromDistrict,
                                      TMSOrderIndexSms.Index_ToProvince,
                                      TMSOrderIndexSms.Index_ToCity,
                                      TMSOrderIndexSms.Index_ToDistrict,
                                      TMSOrderIndexSms.Index_FromTime,
                                      TMSOrderIndexSms.Index_ToTime,
                                      TMSOrderIndexSms.Index_Status,
                                      TMSOrderIndexSms.Index_FromLocation,
                                      TMSOrderIndexSms.Index_ToLocation,
                                      TMSOrderIndexSms.Index_RootOrderID,
                                      TMSOrderIndexSms.Index_Fromtype,
                                      TMSOrderIndexSms.Index_Totype,
                                      TMSOrderIndexSms.Index_StartMsgTime,
                                      TMSOrderIndexSms.Index_ArriveMsgTime,
                                      TMSOrderIndexSms.Index_DeviceCode,
                                      TMSOrderIndexSms.Index_DeviceBindingTime,
                                      TMSOrderIndexSms.Index_ShipMode,
                                      TMSOrderIndexSms.Index_CreateTime,
                                      TMSOrderIndexSms.Index_ToContact,
                                      TMSOrderIndexSms.Index_CreatorCompanyID,
                                      ).filter(TMSOrderIndexSms.Index_Id > sms_track_Index_Id[0],
                                               TMSOrderIndexSms.Index_Status != 32).all()
    if sms_order_list:
        for sms_order in sms_order_list:
            Sendtrack = SmsSendtrack()
            Sendtrack.Index_Id = sms_order[0]
            Sendtrack.Index_Code = sms_order[1]
            Sendtrack.Index_PactCode = sms_order[2]
            Sendtrack.Index_FromProvince = sms_order[3]
            Sendtrack.Index_FromCity = sms_order[4]
            Sendtrack.Index_FromDistrict = sms_order[5]
            Sendtrack.Index_ToProvince = sms_order[6]
            Sendtrack.Index_ToCity = sms_order[7]
            Sendtrack.Index_ToDistrict = sms_order[8]
            Sendtrack.Index_FromTime = sms_order[9]
            Sendtrack.Index_ToTime = sms_order[10]
            Sendtrack.Index_Status_SMS = sms_order[11]
            Sendtrack.Index_FromLocation = sms_order[12]
            Sendtrack.Index_ToLocation = sms_order[13]
            Sendtrack.Index_RootOrderID = sms_order[14]
            Sendtrack.Index_Fromtype = sms_order[15]
            Sendtrack.Index_Totype = sms_order[16]
            Sendtrack.Index_StartMsgTime = sms_order[17]
            Sendtrack.Index_ArriveMsgTime = sms_order[18]
            Sendtrack.Index_DeviceCode = sms_order[19]
            Sendtrack.Index_DeviceBindingTime = sms_order[20]
            Sendtrack.Index_CreateTime = sms_order[22]
            Sendtrack.Index_ToContact = sms_order[23]
            Sendtrack.Index_CreatorCompanyID = sms_order[24]
            Sendtrack.Index_StartMsgStatus = 0
            Sendtrack.Index_ArriveMsgStatus = 0
            Sendtrack.Index_EndStatus = 0
            Sendtrack.Index_Status = 0
            Sendtrack.Index_SignTime = datetime.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            Sendtrack.Index_RealToTime = datetime.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            if sms_order[12] and sms_order[13] and sms_order[12].find(',') > 0 and sms_order[13].find(',') > 0:
                dis = geodesic((sms_order[12].split(',')[1], sms_order[12].split(',')[0]),
                               (sms_order[13].split(',')[1], sms_order[13].split(',')[0])).km
                if dis <= 300:
                    Sendtrack.Index_ShipMode = 1
                else:
                    Sendtrack.Index_ShipMode = 2
            try:
                db.session.add(Sendtrack)
                db.session.commit()
            except Exception as e:
                print(e)
    else:
        print('本次无可同步的数据！')


def get_max_id():  # 获取跟踪表最大的id
    sms_track_Index_Id = db.session.query(SmsSendtrack.Index_Id).filter().order_by(
        SmsSendtrack.ID.desc()).first()
    return sms_track_Index_Id[0]


# def get_sign_id():  # 获取已经签收的订单id
#     max_id = get_max_id()
#     sms_track_Index_Id = db.session.query(SmsSendtrack.Index_Id).filter(SmsSendtrack.Index_Status_SMS == 2,
#                                                                         SmsSendtrack.Index_Status != 4).order_by(
#         SmsSendtrack.ID.desc()).all()  # 获取跟踪表里，同步过来的未签收的订单
#     sms_track_Index_Id_list = [i[0] for i in sms_track_Index_Id]
#     sms_order = db.session.query(TMSOrderIndexSms.Index_Id).filter(
#         TMSOrderIndexSms.Index_Status == 2, TMSOrderIndexSms.Index_Id <= max_id).order_by(
#         TMSOrderIndexSms.Index_Id.desc()).all()  # 获取SMS表里，当前未签收的订单
#     sms_order_list = [i[0] for i in sms_order]
#     # b = list(set(b).difference(set(a)))   # b中有而a中没有的
#     ret_list = list(set(sms_track_Index_Id_list).difference(set(sms_order_list)))
#     return ret_list

def get_bing_time():
    sms_track_Index_Code = db.session.query(SmsSendtrack.Index_RootOrderID).filter(
        SmsSendtrack.Index_Status.between(0, 16), or_(SmsSendtrack.Index_DeviceBindingTime == '1900-01-01 00:00:00.000',
                                                      SmsSendtrack.Index_DeviceBindingTime is None),
        SmsSendtrack.Index_DeviceCode is not None).order_by(
        SmsSendtrack.ID.desc()).all()
    for i in sms_track_Index_Code:
        res2 = db.session.query(SmsSendtrack).filter(SmsSendtrack.Index_RootOrderID == i[0]).first()
        res = db.session.query(TMSOrderIndex.Index_DeviceBindingTime, TMSOrderIndex.Index_CreateTime,
                               TMSOrderIndex.Index_DeviceCode).filter(
            TMSOrderIndex.Index_RootOrderID == i[0], TMSOrderIndex.Index_SrcOrderID == 0).first()
        if res2 and res:
            if str(res[0]) == '1900-01-01 00:00:00':
                if res[2]:
                    res2.Index_DeviceBindingTime = res[1]
                else:
                    b = "{'res':'原始订单未绑定设备！,'code':10001}"
                    res2.Index_NoStartMsgRes = b
                    res2.Index_NoArriveRes = b
                    res2.Index_NoArriveMsgRes = b
                    res2.Index_NoStartMsgCode = 10001
                    res2.Index_NoArriveMsgCode = 10001
                    res2.Index_NoArriveCode = 10001
                    res2.Index_Status = 128
            else:
                res2.Index_DeviceBindingTime = res[0]
        try:
            db.session.commit()
        except Exception as e:
            print(e)


def get_sign_id():  # 获取订单签收状态
    # max_id = get_max_id()
    ret_list = []
    sms_track_Index_Code = db.session.query(SmsSendtrack.Index_RootOrderID).filter(
        SmsSendtrack.Index_Status.between(0, 2)).order_by(
        SmsSendtrack.ID.desc()).all()  #
    for i in sms_track_Index_Code:
        res = db.session.query(TMSOrderIndex.Index_Status, TMSOrderIndex.Index_SignTime).filter(
            TMSOrderIndex.Index_ID == i[0], TMSOrderIndex.Index_SrcOrderID == 0).first()
        if res:
            ret_list.append({'Index_RootOrderID': i[0], 'Index_Status': res[0], "Index_SignTime": res[1]})
    return ret_list


def set_sign_status():  # 设置订单签收状态
    sign_list = get_sign_id()
    for i in sign_list:
        res = db.session.query(SmsSendtrack).filter(SmsSendtrack.Index_RootOrderID == i['Index_RootOrderID']).first()
        res.Index_Status = i['Index_Status']
        res.Index_SignTime = i['Index_SignTime']
        try:
            db.session.commit()
        except Exception as e:
            print(e)


def get_msg_status():  # 获取未签收短信发送情况
    res = db.session.query(SmsSendtrack.Index_RootOrderID).filter(SmsSendtrack.Index_Status_SMS == 2,
                                                                  SmsSendtrack.Index_Status == 2).all()
    for i in res:
        index_order = db.session.query(TMSOrderIndex.Index_StartMsgTime,
                                       TMSOrderIndex.Index_ArriveMsgTime,
                                       TMSOrderIndex.Index_RealToTime,
                                       TMSOrderIndex.Index_CreateTime).filter(
            TMSOrderIndex.Index_RootOrderID == i[0], TMSOrderIndex.Index_SrcOrderID == 0).first()
        if index_order:
            Sendtrack = db.session.query(SmsSendtrack).filter(SmsSendtrack.Index_RootOrderID == i[0]).first()
            Sendtrack.Index_CreateTime = index_order[3]
            if str(index_order[0]) >= str(d):
                if str(index_order[0]) >= str(Sendtrack.Index_StartMsgTime).split('.')[0] and index_order[0]:
                    Sendtrack.Index_StartMsgTime = index_order[0]
                    Sendtrack.Index_StartMsgStatus = 1
            if str(index_order[1]) >= str(d):
                if str(index_order[1]) >= str(Sendtrack.Index_ArriveMsgTime).split('.')[0] and index_order[1]:
                    Sendtrack.Index_ArriveMsgStatus = index_order[1]
                    Sendtrack.Index_ArriveMsgStatus = 1
            if str(index_order[2]) >= str(d):
                if str(index_order[2]) >= str(Sendtrack.Index_RealToTime).split('.')[0] and index_order[2]:
                    Sendtrack.Index_RealToTime = index_order[2]
                    Sendtrack.Index_EndStatus = 1
            try:
                db.session.commit()
            except Exception as e:
                print(e)


def get_status4_msg():  # 获取签收的订单短信发送情况
    res = db.session.query(SmsSendtrack.Index_RootOrderID).filter(SmsSendtrack.Index_Status_SMS == 2,
                                                                  SmsSendtrack.Index_Status.between(4, 16)).all()
    for i in res:
        index_order = db.session.query(TMSOrderIndex.Index_StartMsgTime,
                                       TMSOrderIndex.Index_ArriveMsgTime,
                                       TMSOrderIndex.Index_RealToTime,
                                       TMSOrderIndex.Index_CreateTime).filter(
            TMSOrderIndex.Index_RootOrderID == i[0], TMSOrderIndex.Index_SrcOrderID == 0).first()
        if index_order:
            Sendtrack = db.session.query(SmsSendtrack).filter(SmsSendtrack.Index_RootOrderID == i[0]).first()
            Sendtrack.Index_CreateTime = index_order[3]
            if str(index_order[0]) >= str(d):
                if str(index_order[0]) >= str(Sendtrack.Index_StartMsgTime).split('.')[0] and index_order[0]:
                    Sendtrack.Index_StartMsgTime = index_order[0]
                    Sendtrack.Index_StartMsgStatus = 1
            if str(index_order[1]) >= str(d):
                if str(index_order[1]) >= str(Sendtrack.Index_ArriveMsgTime).split('.')[0] and index_order[1]:
                    Sendtrack.Index_ArriveMsgStatus = index_order[1]
                    Sendtrack.Index_ArriveMsgStatus = 1
            if str(index_order[2]) >= str(d):
                if str(index_order[2]) >= str(Sendtrack.Index_RealToTime).split('.')[0] and index_order[2]:
                    Sendtrack.Index_RealToTime = index_order[2]
                    Sendtrack.Index_EndStatus = 1
            try:
                db.session.commit()
            except Exception as e:
                print(e)


def set_time(imei, start_time, end_time, order_statues, sign_time=None):  # 将时间按3小时一次切割查询
    l = []
    dat = {'start_time': start_time,
           'end_time': end_time,
           'imei': imei
           }
    curr_time = datetime.now()
    lastime = datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')  # 格式化当前时间
    t = start_time
    if order_statues == 2:  # 待签收订单，判断格式化当前时间和到货时间大小
        if str(lastime) >= str(end_time):
            while t <= str(lastime):
                dat['start_time'] = t
                dat['end_time'] = str(datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3))
                t = str(datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3))
                l.append(dat.copy())
        else:
            while t <= str(end_time):
                dat['start_time'] = t
                dat['end_time'] = str(datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3))
                t = str(datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3))
                l.append(dat.copy())
    else:  # 订单为非待签收状态（已签收）
        while t <= str(sign_time):
            dat['start_time'] = t
            dat['end_time'] = str(datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3))
            t = str(datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3))
            l.append(dat.copy())
        l[-1]['end_time'] = sign_time
    return l


def get_location_time(t):
    t = t + +timedelta(hours=8)
    return str(t)


def get_position(data):
    my_list = []
    st = local2utc(str(data['start_time']))
    ed = local2utc(str(data['end_time']))
    res = Position.objects.filter(
        (Q(time__gte=st) & Q(time__lte=ed) & Q(devId=str(data['imei'])))).order_by('time')
    for i in res:
        p_data = {
            'devId': i.devId,
            "longitude": i.longitude,
            "latitude": i.latitude,
            "bLongitude": i.bLongitude,
            "bLatitude": i.bLatitude,
            "type": i.type,
            "time": get_location_time(i.time),
            "speed": i.speed
        }
        my_list.append(p_data)
    return my_list


def get_no_start_msg_reason(index_id,
                            case1):  # 获取没发出发短信的原因 case1表示未发哪种短信
    c1 = 'SmsSendtrack.{}'.format(case1)
    res = db.session.query(SmsSendtrack.Index_Code, SmsSendtrack.Index_FromTime, SmsSendtrack.Index_ToTime,
                           SmsSendtrack.Index_FromLocation, SmsSendtrack.Index_ToLocation,
                           SmsSendtrack.Index_Status_SMS, SmsSendtrack.Index_SignTime,
                           SmsSendtrack.Index_DeviceCode, SmsSendtrack.Index_DeviceBindingTime,
                           SmsSendtrack.Index_Status, SmsSendtrack.Index_CreateTime).filter(
        SmsSendtrack.Index_Id == index_id).first()
    if res:
        try:
            Index_FromTime = res[1]
        except:
            return "{'res': '出发时间缺失!', 'code': -10001}", -10001
        try:
            Index_ToTime = str(res[2]).split('.')[0]
        except:
            return "{'res': '到达时间缺失!', 'code': -10001}", -10001
        try:
            Index_FromLocation = (str(res[3]).split(',')[1], str(res[3]).split(',')[0])
        except:
            return "{'res': '出发地经纬度缺失!', 'code': -10001}", -10001
        try:
            Index_ToLocation = (str(res[4]).split(',')[1], str(res[4]).split(',')[0])
        except:
            return "{'res': '目的地经纬度缺失!', 'code': -10001}", -10001
        try:
            Index_Status_SMS = res[5]
        except:
            return "{'res': 'SMS表订单状态缺失!', 'code': -10001}", -10001
        try:
            Index_SignTime = res[6]
        except:
            return "{'res': 'SMS表签收时间缺失!', 'code': -10001}", -10001
        try:
            Index_DeviceCode = res[7]
        except:
            return "{'res': '设备ID缺失!', 'code': -10001}", -10001
        try:
            Index_DeviceBindingTime = res[8]
        except:
            return "{'res': 'SMS设备绑定时间缺失!', 'code': -10001}", -10001
        Index_Status = res[9]
        Index_CreateTime = res[10]
        up_res = db.session.query(SmsSendtrack).filter(eval(c1) == 0, SmsSendtrack.Index_Id == index_id).first()
        if Index_Status_SMS != '2':
            if case1 == 'Index_StartMsgStatus':
                return "{'res': '绑定设备时，原始订单已不是待签收状态!', 'code': 10001}", 10001
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
        else:
            imei = db.session.query(TMSDevice.Device_IMEICode).filter(TMSDevice.Device_ID == Index_DeviceCode).first()
            # print(str(Index_SignTime).split('.')[0])
            if str(Index_SignTime).split('.')[0] == '1900-01-01 00:00:00' or Index_SignTime is None:  # 订单未签收
                if imei:
                    end_time = (datetime.strptime(res.Index_ToTime.split('.')[0], '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=3))  # .strftime("%Y-%m-%d %H:%M:%S")
                    # now_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
                    if Index_DeviceBindingTime:
                        dat = {'start_time': str(Index_DeviceBindingTime).split('.')[0],
                               'end_time': str(end_time),
                               'imei': imei[0],
                               'order_statues': 2
                               }
                    else:
                        dat = {'start_time': str(Index_FromTime).split('.')[0],
                               'end_time': str(end_time),
                               'imei': imei[0],
                               'order_statues': 2
                               }
                else:
                    return "{'res': '绑定的设备不存在!', 'code': 10001}", 10001
            else:  # 订单已经签收
                if imei:
                    end_time = (datetime.strptime(res.Index_ToTime.split('.')[0], '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=3))  # .strftime("%Y-%m-%d %H:%M:%S")
                    # datetime.strptime(str(res[4]).split('.')[0], "%Y-%m-%d %H:%M:%S") + timedelta(days=3)
                    sign_time = datetime.strptime(str(Index_SignTime).split('.')[0], "%Y-%m-%d %H:%M:%S")
                    if Index_DeviceBindingTime:
                        if sign_time >=end_time:
                            dat = {'start_time': str(Index_DeviceBindingTime).split('.')[0],
                                   'end_time': str(end_time),
                                   'imei': imei[0],
                                   'order_statues': 4,
                                   'sign_time': end_time
                                   }
                        else:
                            dat = {'start_time': str(Index_DeviceBindingTime).split('.')[0],
                                   'end_time': str(end_time),
                                   'imei': imei[0],
                                   'order_statues': 4,
                                   'sign_time': sign_time
                                   }
                    else:
                        if sign_time >= end_time:
                            dat = {'start_time': str(Index_FromTime).split('.')[0],
                                   'end_time': str(end_time),
                                   'imei': imei[0],
                                   'order_statues': 4,
                                   'sign_time': end_time
                                   }
                        else:
                            dat = {'start_time': str(Index_DeviceBindingTime).split('.')[0],
                                   'end_time': str(end_time),
                                   'imei': imei[0],
                                   'order_statues': 4,
                                   'sign_time': sign_time
                                   }
                    if str(dat['sign_time'])< str(dat['start_time']):
                        return "{'res': '订单签收时间在发货时间之前!', 'code': -10001}", -10001
                else:
                    return "{'res': '绑定的设备不存在!', 'code': 10001}", 10001
            print('dat1', dat)
            all_time = set_time(**dat)
            get_m_p = []
            for i in all_time:
                get_m_p = get_m_p + get_position(i)
            if get_m_p:
                return get_m_p, Index_FromLocation, Index_ToLocation, Index_DeviceBindingTime, Index_CreateTime
            else:
                return "{'res': '设备未正常工作!', 'code': -10001}", -10001

    else:
        # up_res = db.session.query(SmsSendtrack).filter(eval(c1) == 0, SmsSendtrack.Index_Id == index_id).first()
        return "{'res': '订单数据无异常!', 'code': 10001}", 10001
# dat = {'start_time': '2020-09-01 10:54:05', 'end_time': '2020-09-10 23:59:01', 'imei': '351608087064973', 'order_statues': 4, 'sign_time': '2020-09-02 16:03:41'}


# 1183160
def get_start_msg_res(index_id, datalist, FromLocation, ToLocation):  # 计算出发短信发送条件
    # a = get_no_start_msg_reason(index_id=index_id, case1='Index_StartMsgStatus')
    datalist = datalist
    FromLocation = FromLocation
    ToLocation = ToLocation
    c = 0
    F_l = []
    T_l = []
    d1_list = []
    d2_list = []
    all_distance = geodesic(FromLocation, ToLocation).km
    for i in datalist:
        # print(i['latitude'], i['longitude'],i['time'])
        distance1 = geodesic((i['latitude'], i['longitude']), FromLocation).km
        distance2 = geodesic((i['latitude'], i['longitude']), ToLocation).km
        d1_list.append(round(distance1, 2))
        d2_list.append(round(distance2, 2))
    l = [d1_list, d2_list]
    if l[0][0] >= all_distance / 3:
        return {'res': '设备第一个定位点超过总距离三分之一！', "code": 10001}, 10001
    else:
        for k in range(1, len(l[0]) - 1):
            if l[0][k] < l[0][k + 1]:
                c = c + 1
                F_l.append(c)
            elif l[0][k - 1] < l[0][k + 1]:
                c = c + 1
                F_l.append(c)
            else:
                c = 0
        for k in range(1, len(l[1]) - 1):
            if l[1][k] > l[1][k + 1]:
                c = c + 1
                T_l.append(c)
            elif l[1][k - 1] > l[1][k + 1]:
                c = c + 1
                T_l.append(c)
            else:
                c = 0
    move_trends = []  # 出发地运动趋势
    end_trends = []  # 目的地距离趋势
    for i, item in enumerate(F_l):
        if item >= 9:
            move_trends.append(i)
    if len(move_trends) >= 2:
        for i, item in enumerate(F_l[:move_trends[0]]):  # i 表示索引，item表示值
            if item >= 9:
                end_trends.append(i)
        for i, item in enumerate(T_l[move_trends[0]:]):
            if item >= 9:
                end_trends.append(i)
        if len(end_trends) >= 2:
            return "{'res': '满足出发短信发送要求！','code': -10001}", -10001
        else:
            return "{'res': '不满足距离目的地越来越近的条件！', 'code': 10001}", 10001
    else:
        return "{'res': '不满足距离出发地越来越远的条件！', 'code': 10001}", 10001


def get_arrive_msg_res(datalist, FromLocation, ToLocation, Transporttype):  # 计算预到达短信发送条件 Transporttype 1表示市内，2表示长途
    c = 0
    T_l = []
    d2_list = []
    for i in datalist:
        distance2 = geodesic((i['latitude'], i['longitude']), ToLocation).km
        d2_list.append(round(distance2, 2))
    if Transporttype == 1:
        # 市内订单
        if any([v < 10 for v in d2_list]):
            return "{'res': '定位距离目的地还剩10公里,符合市内发送预到达短信条件！','code': -10001}", -10001
        else:
            return "{'res': '10公里内没有定位点,不符合市内发送预到达短信条件！''code': 10001}", 10001
    if Transporttype == 2:  # 长途订单
        if any([v < 60 for v in d2_list]):
            return "{'res': '定位距离目的地还剩60公里,符合长途发送预到达短信条件！','code': -10001}", -10001
        else:
            return "{'res': '60公里内没有定位点,不符合长途发送预到达短信条件','code': 10001}", 10001


def get_arrive_status(id):  # 判断设备位置和目的地距离 到达状态
    index_id = id
    res = db.session.query(SmsSendtrack.Index_EndStatus, SmsSendtrack.Index_ToLocation,
                           SmsSendtrack.Index_DeviceCode, SmsSendtrack.Index_FromTime, SmsSendtrack.Index_ToTime,
                           SmsSendtrack.Index_SignTime, SmsSendtrack.Index_CreatorCompanyID,
                           SmsSendtrack.Index_Status).filter(index_id == SmsSendtrack.Index_Id,
                                                             SmsSendtrack.Index_EndStatus == 0).first()
    all_dis = []
    d2_list = []
    count = 0
    order_list = ['1', ' 2']
    order_list2 = ['4', ' 8', '16']
    print(index_id, res[-1])
    # distance2 = geodesic((i['latitude'], i['longitude']), ToLocation).km   孩子王公司 ID 2353
    if res[-1] == '2' or res[-1] == '1':  # 判断是否到达, 订单未触发到达且订单未签收
        devid = db.session.query(TMSDevice.Device_IMEICode).filter(TMSDevice.Device_ID == res[2]).first()  # 获取设备码
        dat = {'start_time': str(res[3]).split('.')[0],
               'end_time': datetime.strptime(str(res[4]).split('.')[0], "%Y-%m-%d %H:%M:%S")+timedelta(days=3),
               'imei': devid[0],
               'order_statues': 2
               }
        all_time = set_time(**dat)
        get_m_p = []
        for i in all_time:
            get_m_p = get_m_p + get_position(i)
        if get_m_p:
            for i in get_m_p:
                distance2 = geodesic((i['latitude'], i['longitude']), (eval(res[1])[1], eval(res[1])[0])).km
                d2_list.append(round(distance2, 2))
            for j in d2_list:
                if j <= 3:
                    count = count + 1
                    all_dis.append(count)
                else:
                    count = 0
            if res[-2] == 2353:
                if all_dis:
                    return "{'res': '设备有1个定位点距离目的距离小于等于3公里！', 'code': -10001}", -10001
                else:
                    return "{'res': '设备没有定位点距离目的距离小于等于3公里！', 'code': 10001}", 10001
            else:
                if 5 in all_dis:
                    return "{'res': '设备超过5个定位点距离目的距离小于等于3公里！', 'code': -10001}", -10001
                else:
                    return "{'res': '设备没有超过5个定位点距离目的距离小于等于3公里！', 'code': 10001}", 10001
        else:
            return "{'res': '设备未正常工作！', 'code': -10001}", -10001
    if res[-1] == '4' or res[-1] == '8' or res[-1] == '16':  # 判断是否到达, 订单未触发到达且订单已签收
        # datetime.strptime(res.Index_ToTime.split('.')[0], '%Y-%m-%d %H:%M:%S') + timedelta(
        #                         days=3)
        devid = db.session.query(TMSDevice.Device_IMEICode).filter(TMSDevice.Device_ID == res[2]).first()  # 获取设备码
        dat = {'start_time': str(res[3]).split('.')[0],
               'end_time': str(res[4]).split('.')[0],
               'sign_time': str(res[5]).split('.')[0],
               'imei': devid[0],
               'order_statues': 4
               }
        if dat['sign_time'] > dat['start_time']:
            if (datetime.strptime(dat['sign_time'], '%Y-%m-%d %H:%M:%S')-datetime.strptime(dat['start_time'], '%Y-%m-%d %H:%M:%S')).days <=3:
                dat = dat
            else:
                dat['sign_time'] = datetime.strptime(dat['start_time'], '%Y-%m-%d %H:%M:%S') + timedelta(days=3)
            all_time = set_time(**dat)
            get_m_p = []
            count = 0
            for i in all_time:
                get_m_p = get_m_p + get_position(i)
            if get_m_p:
                for i in get_m_p:
                    distance2 = geodesic((i['latitude'], i['longitude']), (eval(res[1])[1], eval(res[1])[0])).km
                    d2_list.append(round(distance2, 2))
                for j in d2_list:
                    if j <= 3:
                        count = count + 1
                        all_dis.append(count)
                    else:
                        count = 0
                if 5 in all_dis:
                    return "{'res': '设备超过5个定位点距离目的距离小于等于3公里！', 'code': -10001}", -10001
                else:
                    return "{'res': '设备没有超过5个定位点距离目的距离小于等于3公里！', 'code': 10001}", 10001
            else:
                return "{'res': '设备未正常工作！', 'code': -10001}", -10001

        else:
            return "{'res': '签收时间大于发货时间！', 'code': -10001}", -10001


def judge_location_type(index_id):  # 判断出发和目的地定位类型,trans_type 1表示市内，2表示长途
    res = db.session.query(SmsSendtrack.Index_Fromtype, SmsSendtrack.Index_FromCity, SmsSendtrack.Index_Totype,
                           SmsSendtrack.Index_ToCity).filter(SmsSendtrack.Index_Id == index_id).first()
    l = []
    if res[1] == res[3]:
        l.append({"Fromtype": res[0], "trans_type": 1, "Totype": res[2]})
    else:
        l.append({"Fromtype": res[0], "trans_type": 2, "Totype": res[2]})
    return l


def process_control(**kwargs):  # 流程控制入口
    # 首先获取定位类型
    index_id = int(kwargs['index_id'])
    Index_StartMsgStatus = kwargs['case1']
    Index_ArriveMsgStatus = kwargs['case2']
    Index_EndStatus = ['case3']
    # loc_type = judge_location_type(index_id)
    res = db.session.query(SmsSendtrack).filter(SmsSendtrack.Index_Id == index_id,
                                                SmsSendtrack.Index_Status.between(2, 16)).first()
    # 获取对应订单的定位数据，出发地和目的地经纬度，绑定时间
    a = get_no_start_msg_reason(index_id, Index_StartMsgStatus)
    if len(a) == 5:
        datalist = a[0]
        Index_FromLocation = a[1]
        Index_ToLocation = a[2]
        Index_DeviceBindingTime = a[3]
        Index_CreateTime = a[4]
        # 判断出发地和目的地直线距离单位KM
        from_to_dis = round(geodesic(Index_FromLocation, Index_ToLocation).km, 2)
        # print(from_to_dis, Index_CreateTime, Index_DeviceBindingTime)
        # if re.match(r'1[3,4,5,7,8]\d{9}',n): 正则判断联系电话是不是手机号码
        if res:
            ToContact = res.Index_ToContact
            if res.Index_CreatorCompanyID == 1925:  # TOP订单，截取前面11位
                ToContact = ToContact[:10]
            ShipMode = res.Index_ShipMode  # 1表示市内订单，2表示长途订单
            if ShipMode == 1:  # 市内订单
                if res.Index_StartMsgStatus == 0:  # 没有出发短信的订单
                    if from_to_dis <= 20:  # 市内订单 极短距离
                        a = "{'res': '订单距离小于20公里，无出发短信!', 'code': 10001}"
                        res.Index_NoStartMsgRes = str(a)
                        res.Index_NoStartMsgCode = 10001
                    if res.Index_CreateTime != Index_DeviceBindingTime:
                        a = "{'res': '补绑的市内订单，无出发短信!', 'code': 10001}"
                        res.Index_NoStartMsgRes = str(a)
                        res.Index_NoStartMsgCode = 10001
                    else:  # 直线距离超过20公里
                        if re.match(r'1[3,4,5,7,8]\d{9}', ToContact) and len(ToContact) == 11:
                            print('1出发短信', datetime.now())
                            a, code = get_start_msg_res(index_id, datalist, Index_FromLocation, Index_ToLocation)
                            print('1出发短信', datetime.now())
                            res.Index_NoStartMsgRes = str(a)
                            res.Index_NoStartMsgCode = code
                        else:
                            res.Index_NoStartMsgRes = "{'res':'号码不是手机号,无法获取出发短信！','code':10001}"
                            res.Index_NoStartMsgCode = 10001
                else:
                    res.Index_NoStartMsgRes = "{'res': '出发短信已发送！', 'code': 10001}"
                    res.Index_NoStartMsgCode = 10001
                if res.Index_ArriveMsgStatus == 0:  # 没有预到达短信
                    if re.match(r'1[3,4,5,7,8]\d{9}', ToContact) and len(ToContact) == 11:
                        print('1预到达短', datetime.now())
                        b, code = get_arrive_msg_res(datalist=datalist, FromLocation=Index_FromLocation,
                                                     ToLocation=Index_ToLocation,
                                                     Transporttype=1)
                        print('1预到达短', datetime.now())
                        res.Index_NoArriveMsgRes = str(b)
                        res.Index_NoArriveMsgCode = code
                    else:
                        res.Index_NoArriveMsgRes = "{'res':'号码不是手机号,无法获取预到达短信！','code':10001}"
                        res.Index_NoArriveMsgCode = 10001
                else:
                    res.Index_NoArriveMsgRes = "{'res': '预到达短信已发送！', 'code': 10001}"
                    res.Index_NoArriveMsgCode = 10001
                if res.Index_EndStatus == 0:  # 没有触发达到状态
                    print('1到达', datetime.now(), index_id)
                    c, code = get_arrive_status(index_id)
                    print('1到达', datetime.now())
                    res.Index_NoArriveRes = str(c)
                    res.Index_NoArriveMsgCode = code
                else:
                    res.Index_NoArriveRes = "{'res': '已触发已到达状态！', 'code': 10001}"
                    res.Index_NoArriveMsgCode = 10001
            if ShipMode == 2:  # 长途订单
                if res.Index_StartMsgStatus == 0:
                    if re.match(r'1[3,4,5,7,8]\d{9}', ToContact) and len(ToContact) == 11:
                        print('2出发短信', datetime.now())
                        a, code = get_start_msg_res(index_id, datalist, Index_FromLocation, Index_ToLocation)
                        print('2出发短信', datetime.now())
                        res.Index_NoStartMsgRes = str(a)
                        res.Index_NoStartMsgCode = code
                    else:
                        res.Index_NoStartMsgRes = "{'res':'号码不是手机号,无法获取出发短信！','code':10001}"
                        res.Index_NoStartMsgCode = 10001
                else:
                    res.Index_NoStartMsgRes = "{'res': '出发短信已发送！', 'code': 10001}"
                    res.Index_NoStartMsgCode = 10001
                if res.Index_ArriveMsgStatus == 0:  # 没有预到达短信
                    if re.match(r'1[3,4,5,7,8]\d{9}', ToContact) and len(ToContact) == 11:
                        print('2预到达短', datetime.now())
                        b, code = get_arrive_msg_res(datalist=datalist, FromLocation=Index_FromLocation,
                                                     ToLocation=Index_ToLocation,
                                                     Transporttype=2)
                        print('2预到达短', datetime.now())
                        res.Index_NoArriveMsgRes = str(b)
                        res.Index_NoArriveMsgCode = code
                    else:
                        res.Index_NoArriveMsgRes = "{'res':'号码不是手机号,无法获取预到达短信！','code':10001}"
                        res.Index_NoArriveMsgCode = 10001
                else:
                    res.Index_NoArriveMsgRes = "{'res': '预到达短信已发送！', 'code': 10001}"
                    res.Index_NoArriveMsgCode = 10001
                if res.Index_EndStatus == 0:  # 没有触发达到状态
                    print('2到达', datetime.now())
                    c, code = get_arrive_status(index_id)
                    print('2到达', datetime.now())
                    res.Index_NoArriveRes = str(c)
                    res.Index_NoArriveCode = code
                else:
                    res.Index_NoArriveRes = "{'res': '已触发已到达状态！', 'code': 10001}"
                    res.Index_NoArriveCode = 10001
        else:
            print('{}订单已经关闭'.format(index_id))
            return False
    else:
        print(2222)
        b, code = get_no_start_msg_reason(index_id, Index_StartMsgStatus)
        if res:
            res.Index_NoStartMsgRes = b
            res.Index_NoArriveRes = b
            res.Index_NoArriveMsgRes = b
            res.Index_NoArriveMsgCode = code
            res.Index_NoStartMsgCode = code
            res.Index_NoArriveCode = code
        else:
            print('{}订单已经关闭'.format(index_id))
            return False
    try:
        res.Index_UpdateTime = datetime.now()
        print(res.Index_NoStartMsgRes)
        print(res.Index_NoArriveMsgRes)
        print(res.Index_NoArriveRes)
        print(datetime.now())
        db.session.commit()
    except Exception as e:
        print(e, 1111)


def get_sign_order_sms():
    res = db.session.query(SmsSendtrack.Index_Id).filter(SmsSendtrack.Index_DeviceCode is not None,
                                                         SmsSendtrack.Index_SignTime > SmsSendtrack.Index_UpdateTime,
                                                         SmsSendtrack.Index_Status.between(4, 16)).order_by(
        SmsSendtrack.Index_Id).all()  # 签收时间在更新订单短信之前则再次更新订单数据
    c = 0
    all_order = len(res)
    for i in res:
        c = c + 1
        print("一共{}笔订单，正在处理第{}笔订单！".format(all_order, c), i[0])
        data = {"index_id": i[0],
                'case1': 'Index_StartMsgStatus',
                'case2': 'Index_ArriveMsgStatus',
                'case3': 'Index_EndStatus',
                }
        process_control(**data)


def get_not_sign_order_sms():
    res = db.session.query(SmsSendtrack.Index_Id).filter(SmsSendtrack.Index_DeviceCode is not None,
                                                         SmsSendtrack.Index_Status.between(0, 2)).order_by(
        SmsSendtrack.Index_Id).all()
    c = 0
    all_order = len(res)
    for i in res:
        c = c + 1
        print("一共{}笔订单，正在处理第{}笔订单！".format(all_order, c))
        data = {"index_id": i[0],
                'case1': 'Index_StartMsgStatus',
                'case2': 'Index_ArriveMsgStatus',
                'case3': 'Index_EndStatus',
                }
        process_control(**data)


def get_abnormal_start_order(page, size):  # 获取已签收出发短信异常订单
    res = db.session.query(SmsSendtrack.Index_PactCode, SmsSendtrack.Index_FromTime, SmsSendtrack.Index_ToTime,
                           SmsSendtrack.Index_DeviceCode, SmsSendtrack.Index_Fromtype, SmsSendtrack.Index_Totype,
                           SmsSendtrack.Index_NoStartMsgRes, SmsSendtrack.Index_NoArriveMsgRes,
                           SmsSendtrack.Index_Status).filter(
        SmsSendtrack.Index_Status != 32,
        SmsSendtrack.Index_Status.between(4, 16),
        SmsSendtrack.Index_NoStartMsgCode == -10001).paginate(page, size, error_out=False)
    start_list = []
    for i in res.items:
        if i[6] and eval(i[6])['code'] == -10001:  # 出发短信异常订单
            DeviceCode = db.session.query(TMSDevice.Device_IMEICode).filter(TMSDevice.Device_ID == i[3]).first()
            start_list.append(
                {'Index_PactCode': i[0], 'Index_FromTime': str(i[1]).split('.')[0],
                 'Index_ToTime': str(i[2]).split('.')[0], 'Index_DeviceCode': DeviceCode[0],
                 'Index_Fromtype': i[4], 'Index_Totype': i[5], 'Index_NoStartMsgRes': i[6], 'Index_Status': i[7]})
    return {'datelist': start_list, 'total_page': res.pages, 'total': res.total}


def get_abnormal_arrive_order(page, size):  # 获取已签收到达短信异常订单
    res = db.session.query(SmsSendtrack.Index_PactCode, SmsSendtrack.Index_FromTime, SmsSendtrack.Index_ToTime,
                           SmsSendtrack.Index_DeviceCode, SmsSendtrack.Index_Fromtype, SmsSendtrack.Index_Totype,
                           SmsSendtrack.Index_NoStartMsgRes, SmsSendtrack.Index_NoArriveMsgRes,
                           SmsSendtrack.Index_Status).filter(
        SmsSendtrack.Index_Status != 32,
        SmsSendtrack.Index_Status.between(4, 16),
        SmsSendtrack.Index_NoArriveMsgCode == -10001).paginate(page, size, error_out=False)
    arr_list = []
    for i in res.items:
        if i[6] and eval(i[6])['code'] == -10001:  # 出发短信异常订单
            DeviceCode = db.session.query(TMSDevice.Device_IMEICode).filter(TMSDevice.Device_ID == i[3]).first()
            arr_list.append(
                {'Index_PactCode': i[0], 'Index_FromTime': str(i[1]).split('.')[0],
                 'Index_ToTime': str(i[2]).split('.')[0], 'Index_DeviceCode': DeviceCode[0],
                 'Index_Fromtype': i[4], 'Index_Totype': i[5], 'Index_NoStartMsgRes': i[6], 'Index_Status': i[7]})
    return {'datelist': arr_list, 'total_page': res.pages, 'total': res.total}


# 1925
# get_sms_order()
# print(get_abnormal_start_order(1, 2), get_abnormal_arrive_order(1, 2))
# 1172984
# def test_order_sms():
#     data = {"index_id": '1183316',
#             'case1': 'Index_StartMsgStatus',
#             'case2': 'Index_ArriveMsgStatus',
#             'case3': 'Index_EndStatus',
#             }
#     process_control(**data)
#
#
# test_order_sms()
# get_sms_order()
while 1:
    print('-------------开始同步SMS表订单数据----------------')
    get_sms_order()
    print('-------------------同步完成----------------------')
    print('------------开始同步订单表设备绑定时间--------------')
    get_bing_time()
    print('-------------------同步完成----------------------')
    print('--------------开始同步订单签收状态-----------------')
    set_sign_status()
    print('--------------------同步完成---------------------')
    print('------------开始同步未签收订单短信状态--------------')
    get_msg_status()
    print('--------------------同步完成---------------------')
    print('------------开始同步已签收订单短信状态--------------')
    get_status4_msg()
    print('--------------------同步完成----------------------')
    print('-------------开始同步签收订单短信情况---------------')
    get_sign_order_sms()
    print('--------------------同步完成----------------------')
    print('-------------开始同步未签收订单短信情况--------------')
    get_not_sign_order_sms()
    print('--------------------同步完成----------------------')
    sleep(1800)

# p = ThreadPoolExecutor()  # 线程池 #如果不给定值，默认cup*5
# for i in range(10):  # 10个任务 # 线程池效率高了
#     obj = p.submit(get_all_index_id)  # 相当于apply_async异步方法
#     print(obj.result())
# p.shutdown()  # 默认有个参数wite=True (相当于close和join)

# process_control(index_id='1183162', case1='Index_StartMsgStatus') 1183200
# a = get_no_start_msg_reason(index_id='1183200', case1='Index_StartMsgStatus')
# a = get_arrive_status(index_id=1183162)  1183197
# print(a)
# data = {"index_id": '1183203',
#         'case1': 'Index_StartMsgStatus',
#         'case2': 'Index_ArriveMsgStatus',
#         'case3': 'Index_EndStatus',
#         }
# process_control(**data)
# get_no_start_msg_reason(index_id=1183200, case1='Index_StartMsgStatus')
#
# get_start_msg_res(data['index_id'])
# get_arrive_status(data['index_id'])
# print(dd)
# dd = get_start_msg_res(index_id=1183162)
# print(dd)
# a = get_no_start_msg_reason(index_id='1183162', case1='Index_StartMsgStatus')
# ps = a[0]
# FromLocation = a[1]
# ToLocation = a[2]
# get_start_msg_res(ps, FromLocation, ToLocation)
# print(get_arrive_msg_res(ps, FromLocation, ToLocation, Transporttype=2))
# def get_no_arrive_msg_reason(index_id):  # 获取没达到发短信的原因
#     M_P = More_Position()
#     get_m_p = M_P.get_more_position()
#     res = db.session.query(SmsSendtrack.Index_Code).filter(SmsSendtrack.Index_ArriveMsgStatus == 0).all()
#     if res.Index_Status_SMS != 2:
#         return {'res': '绑定设备时，原始订单已不是待签收状态!'}
#
#
# def get_no_end_status_reason(index_id):  # 获取没达到发的原因
#     M_P = More_Position()
#     get_m_p = M_P.get_more_position()
#     res = db.session.query(SmsSendtrack.Index_Code).filter(SmsSendtrack.Index_StartMsgStatus == 0).all()
#     if res.Index_Status_SMS != 2:
#         return {'res': '绑定设备时，原始订单已不是待签收状态!'}


# (28.2053616,113.0851055),(28.71472654259431,115.79184538078704)


# set_time(imei='351608086050742', from_time='2020-07-01 00:00:00', to_time='2020-07-02 00:00:00', order_statues=4,
#          sign_time='2020-07-04 00:00:00')

# data = {'start_time': '2020-07-07 00:00:00', 'end_time': '2020-07-21 00:00:00', 'imei': "351608086036022"}
# a = get_position(data)
# # print(a)
# tt = (35.52921512762575, 116.77639203399478)
# for i in a:
#     d = geodesic((i['latitude'], i['longitude']), tt).km
#     d2 = round(d, 2)
#     if d2 <= 1:
#         print(d2, i['time'])
