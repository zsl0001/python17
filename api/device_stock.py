import sys
import datetime

sys.path.append("..")
# from datetime import datetime, timedelta

from sqlalchemy import extract, or_

from models import db, DeviceStock, TMSCompany, TMSSale, StockLog, User


def set_log(IMEI, Creator_Name, Sales_Name, Content, Set_time):
    log = StockLog()
    log.IMEI = IMEI
    log.Creator_Name = Creator_Name
    log.Sales_Name = Sales_Name
    log.Insert_Time = Set_time
    for content in Content:
        log.Content = content
        try:
            db.session.add(log)
            db.session.commit()
            return {'res': '修改成功!', 'code': 1001}
        except Exception as e:
            print(e)
            return {'res': '修改失败!', 'code': -1001}


class device_stock:
    def __init__(self, data=None, ip=None):
        self.data = data
        self.ip = ip

    def add_stock(self):
        l = []
        ss_list = []
        fail_list = []
        for i in self.data:
            useraccount = i['useraccount']
            username = i['username']
            res = DeviceStock()
            log = StockLog()
            res.Device_IMEI = i['imei']
            count = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI == i['imei']).first()
            # print(i['imei'], count.Device_IMEI)
            print(count is None)
            if count:
                fail_list.append({'res': '新增失败，设备已存在!', 'code': -1001, 'imei': i['imei']})
            else:
                print(i['imei'])
                res.Device_Inserttime = datetime.datetime.now()
                log.IMEI = i['imei']
                log.Insert_Time = datetime.datetime.now()
                log.Creator_Name = username
                log.Content = '{}将设备码为{}的设备录入了系统，时间为{}，录入地IP为{}.'.format(username, i['imei'],
                                                                         datetime.datetime.now().strftime(
                                                                             "%Y-%m-%d %H:%M:%S"),
                                                                         self.ip)
                try:
                    db.session.add(log)
                    db.session.add(res)
                    db.session.commit()
                    ss_list.append({'res': '新增成功!', 'code': 1001, 'imei': i['imei']})
                except Exception as e:
                    print(e)
                    return {'res': '新增失败', 'code': -1001, }
        if len(fail_list) == 0:
            l = ss_list
            data = {'datalist': [],
                    'res': '新增成功!',
                    'code': 1001
                    }
        else:
            l = fail_list
            data = {'datalist': l,
                    'res': '新增失败，设备已经存在!',
                    'code': -1001
                    }
        return data

    def get_all_sales(self):  # 输入销售名字时，模糊搜索符合条件的销售列表
        res = db.session.query(User).filter(User.sales_name.like('%' + self.data['sales_name'] + '%'),
                                            User.is_disable == 0).all()
        l = []
        for i in res:
            l.append({'sales_name': i.sales_name, 'user_id': i.id, 'user_name': i.username})
        return l

    def init_stock(self):  # 初始化修改库存表
        fail_list = []
        try:
            for i in self.data:
                if 'sales_status' in i:
                    status = i['sales_status']
                else:
                    status = 1
                log = StockLog()
                res = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI == i['imei'],
                                                           DeviceStock.is_disable == 0).first()
                if res:
                    useraccount = i['useraccount']
                    username = i['username']
                    cp_rs = db.session.query(TMSCompany).filter(
                        TMSCompany.Company_ClientCode == i['Company_ClientCode'],
                        TMSCompany.Company_Status == 2,
                        TMSCompany.Company_Invalid == 0).first()
                    if cp_rs:
                        res.Sales_Name = i['sales_name']
                        res.User_ID = i['id']
                        res.Company_ID = cp_rs.Company_ID
                        res.Company_Name = cp_rs.Company_Name
                        res.Sales_Time = i['Sales_Time']
                        res.Sales_Statues = status
                        res.Flow_Fee_Start_Time = i['Flow_Fee_Start_Time']
                        res.Flow_Fee_End_Time = i['Flow_Fee_End_Time']
                        res.Company_ClientCode = i['Company_ClientCode']
                        log.IMEI = i['imei']
                        log.Creator_Name = useraccount
                        log.Sales_Name = username
                        log.Insert_Time = datetime.datetime.now()
                        log.Content = '{}将设备码为{}的设备分配给{},所属销售为{},销售时间为{},资讯费计时开始时间为{},结束时间为{},操作时间为{},操作地所在IP为{}。'.format(
                            i['user_name'],
                            i['imei'], cp_rs.Company_Name, username, i['Sales_Time'],
                            i['Flow_Fee_Start_Time'],
                            i['Flow_Fee_End_Time'],
                            log.Insert_Time,
                            self.ip)
                        try:
                            db.session.add(log)
                            db.session.add(res)
                            db.session.commit()
                        except Exception as e:
                            print(e)
                            return {'res': '修改失败!', 'code': -1001}
                    else:
                        return {'res': '公司编号错误!', 'code': -1001}
                else:
                    fail_list.append({'imei': i['imei'], 'code': -1001, 'res': '设备不存在，请先导入库存!'})
            if len(fail_list) != 0:
                data = {'datalist': fail_list, 'res': '修改失败!', 'code': -1001}
            else:
                data = {'datalist': [], 'res': '修改成功!', 'code': 1001}
            return data
        except KeyError as e:
            print(e)
            return {'res': '参数错误!', 'code': -1001}

    def get_stock_remarks(self):
        pass

    def search_stock(self):
        try:
            page = self.data['page']
            size = self.data['size']
        except Exception as e:
            print(e)
            return {'res': '参数错误！', "code": -10001}
        if 'imei' in self.data.key():
            res = db.session.query(DeviceStock).filter(
                DeviceStock.Device_IMEI.like('%' + self.data['imei'] + '%'), DeviceStock.is_disable == 0).paginate(
                int(page),
                int(size), False)
        if 'company_name' in self.data.key():
            res = db.session.query(DeviceStock).filter(
                DeviceStock.Company_Name.like('%' + self.data['company_name'] + '%',
                                              DeviceStock.is_disable == 0)).paginate(int(page),
                                                                                     int(size), False)
        if 'sales_name' in self.data.key():
            res = db.session.query(DeviceStock).filter(
                DeviceStock.Sales_Name.like('%' + self.data['sales_name'] + '%'), DeviceStock.is_disable == 0).paginate(
                int(page),
                int(size), False)
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            l.append({'imei': i.Device_IMEI, 'sales_name': i.Sales_Name, 'company_name': i.Company_Name,
                      'sales_time': str(i.Sales_Time).split('.')[0],
                      'Flow_Fee_Start_Time': str(i.Flow_Fee_Start_Time).split('.')[0],
                      'Flow_Fee_End_Time': str(i.Flow_Fee_End_Time).split('.')[0], 'sales_status': i.Sales_Statues})
        rs_data['datalist'] = l
        return rs_data

    def get_all_stock(self):
        try:
            page = self.data['page']
            size = self.data['size']
        except Exception as e:
            print(e)
            return {'res': '参数错误！', "code": -10001}
        res = self.search_my_stock(is_disable=0)
        if 'sales_status' in self.data.keys():
            res = res.filter(DeviceStock.Sales_Statues == self.data['sales_status'])
        res = res.order_by(DeviceStock.Device_Inserttime.desc()).paginate(int(page), int(size), False)
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            l.append({'imei': i.Device_IMEI, 'sales_name': i.Sales_Name, 'company_name': i.Company_Name,
                      'sales_time': str(i.Sales_Time).split('.')[0],
                      'Flow_Fee_Start_Time': str(i.Flow_Fee_Start_Time).split('.')[0],
                      'Flow_Fee_End_Time': str(i.Flow_Fee_End_Time).split('.')[0], 'sales_status': i.Sales_Statues})
        rs_data['datalist'] = l
        return rs_data

    def set_sale_status(self):  # 修改销售状态
        try:
            id = self.data['user_id']
            imei = self.data['imei']
            sales_statues = self.data['sales_statues']
            useraccount = self.data['useraccount']
            username = self.data['username']
        except Exception as e:
            print(e)
            return {'res': '参数错误！', "code": -10001}
        # u_id = db.session.query(User).filter(User.id == id, User.is_disable == 0).first()
        set_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI == imei, DeviceStock.is_disable == 0).first()
        if sales_statues not in [0, 1, 2]:
            return {'res': '参数错误！', "code": -10001}
        else:
            res.Sales_Statues = sales_statues
            if sales_statues == 1:
                print(sales_statues)
                content = f'{username}将设备编码为{imei}的设备,从未售改成了已售,修改时间为{set_time},修改地ip为{self.ip}.'
                set_log(IMEI=imei, Creator_Name=useraccount, Sales_Name=username, Set_time=set_time,
                        Content=[content])
            elif sales_statues == 2:
                print(sales_statues)
                content = f'{username}将设备编码为{imei}的设备,从未售改成了租用,修改时间为{set_time},修改地ip为{self.ip}.'
                set_log(IMEI=imei, Creator_Name=useraccount, Sales_Name=username, Set_time=set_time,
                        Content=[content])
            else:
                print(sales_statues)
                try:
                    remarks = self.data['remarks']
                except Exception as e:
                    print(e)
                    return {'res': '参数错误！', "code": -10001}
                old_remarks = res.Remarks
                res.Remarks = remarks
                res.Remark_Time = set_time
                content = f'{username}将设备编码为{imei}的设备,从已售改成了未售,修改时间为{set_time},修改地ip为{self.ip}.'
                rm = f'{username}将设备编码为{imei}的设备的备注从{old_remarks}修改为{remarks},修改时间为{set_time},修改地ip为{self.ip}.'
                set_log(IMEI=imei, Creator_Name=useraccount, Sales_Name=username, Set_time=set_time,
                        Content=[content, rm])
        try:
            db.session.commit()
            return {'res': '修改成功!', 'code': 1001}
        except Exception as e:
            print(e)
            return {'res': '修改失败!', 'code': -1001}

    def set_disable_status(self):  # 修改是否可售 0表示可售 1表示不可售
        try:
            set_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            imei = self.data['imei']
            is_disable = self.data['is_disable']
            id = self.data['user_id']
            remarks = self.data['remarks']
            useraccount = self.data['useraccount']
            username = self.data['username']
        except Exception as e:
            print(e)
            return {'res': '参数错误！', "code": -10001}
        # u_id = db.session.query(User).filter(User.id == id, User.is_disable == 0).first()
        res = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI == imei).first()
        if res:
            old_remarks = res.Remarks
        else:
            old_remarks = ''
        if is_disable not in [0, 1] or res.is_disable == is_disable:
            return {'res': '参数错误！', "code": -10001}
        else:
            res.is_disable = is_disable
            res.Remarks = remarks
            res.Remark_Time = set_time
            if is_disable == 1:
                content = f'{username}将设备编码为{imei}的设备,从销售列表中移除，变为不可售状态,修改时间为{set_time},修改地ip为{self.ip}.'
                rm = f'{username}将设备编码为{imei}的设备的备注从{old_remarks}修改为{remarks},修改时间为{set_time},修改地ip为{self.ip}.'
                set_log(IMEI=imei, Creator_Name=useraccount, Sales_Name=username, Set_time=set_time,
                        Content=[content, rm])
            else:
                r = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI == imei,
                                                         DeviceStock.is_disable == 0).all()
                content = f'{username}将设备编码为{imei}的设备,加入待售列表，修改时间为{set_time},修改地ip为{self.ip}.'
                rm = f'{username}将设备编码为{imei}的设备的备注从{old_remarks}修改为{remarks},修改时间为{set_time},修改地ip为{self.ip}.'
                set_log(IMEI=imei, Creator_Name=useraccount, Sales_Name=username, Set_time=set_time,
                        Content=[content, rm])
        try:
            db.session.commit()
            return {'res': '修改成功!', 'code': 1001}
        except Exception as e:
            print(e)
            return {'res': '修改失败!', 'code': -1001}

    def get_set_log(self):  # 获取设备操作日志
        try:
            page = self.data['page']
            size = self.data['size']
            imei = self.data['imei']
        except Exception as e:
            print(e)
            return {'res': '参数错误！', "code": -10001}
        res = db.session.query(StockLog).filter(StockLog.IMEI == imei).order_by(StockLog.Insert_Time.desc()).paginate(
            int(page), int(size), False)
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            l.append({'log_info': i.Content})
        rs_data['datalist'] = l
        return rs_data

    def get_disable_devices(self):  # 获取历史禁售列表
        try:
            page = self.data['page']
            size = self.data['size']
        except Exception as e:
            print(e)
            return {'res': '参数错误！', "code": -10001}
        res = self.search_my_stock(is_disable=1)
        if 'sales_status' in self.data.keys():
            res = res.filter(DeviceStock.Sales_Statues == self.data['sales_status'])
        res = res.order_by(DeviceStock.Device_Inserttime.desc()).paginate(int(page), int(size), False)
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            l.append({'imei': i.Device_IMEI, 'sales_name': i.Sales_Name, 'company_name': i.Company_Name,
                      'sales_time': str(i.Sales_Time).split('.')[0],
                      'Flow_Fee_Start_Time': str(i.Flow_Fee_Start_Time).split('.')[0],
                      'Flow_Fee_End_Time': str(i.Flow_Fee_End_Time).split('.')[0], 'sales_status': i.Sales_Statues})
        rs_data['datalist'] = l
        return rs_data

    def renew_flow_fee(self):  # 流量续费
        l = []
        dat = {'res': '修改失败!', 'datalist': '','code':-1001}
        for i in self.data:
            try:
                imei = i['imei']
                new_end_time = i['end_time']
                id = i['id']
                useraccount = i['useraccount']
                username = i['username']
                set_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(e)
                return {'res': '参数错误!', 'code': -1001}
            res = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI == imei,
                                                       DeviceStock.is_disable == 0).first()
            if res:
                res.Flow_Fee_End_Time = new_end_time
                # u_id = db.session.query(User).filter(User.id == id, User.is_disable == 0).first()
                content = f'{username}将编码为{imei}的设备进行了续费新的资讯费到期时间为{new_end_time}，修改时间为{set_time}，修改地IP为{self.ip}.'
                set_log(IMEI=imei, Creator_Name=useraccount, Sales_Name=username, Set_time=set_time,
                        Content=[content])
                try:
                    db.session.commit()
                    # return {'res': '修改成功!', 'code': 1001}
                except Exception as e:
                    print(e)
                    return {'res': '修改失败!', 'code': -1001}
            else:
                l.append({'imei': imei, 'res': '设备不存在，请先维护库存!', 'code': -1001})
        dat['datalist'] = l
        if len(l) == 0:
            return {'res': '修改成功！','code': 1001}
        else:
            return dat

    def get_remarks(self):
        try:
            imei = self.data['imei']
        except Exception as e:
            print(e)
            return {'res': '参数错误!', 'code': -1001}
        res = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI == imei).first()
        return {'res': res.Remarks, 'code': 1001, 'time': str(res.Remark_Time).split('.')[0]}

    def get_expiring_soon(self):  # 获取30内资讯费即将到期的设备列表
        try:
            page = self.data['page']
            size = self.data['size']
        except Exception as e:
            print(e)
            return {'res': '参数错误！', "code": -10001}
        res = self.search_my_stock(is_disable=0)
        if 'sales_status' in self.data.keys():
            res = res.filter(DeviceStock.Sales_Statues == self.data['sales_status'])
        set_time = datetime.datetime.now() + datetime.timedelta(days=30)
        res = res.filter(DeviceStock.is_disable == 0,
                         (DeviceStock.Flow_Fee_End_Time <= set_time))
        # (extract('day', DeviceStock.Flow_Fee_End_Time) - set_time) <= 30)
        res = res.order_by(DeviceStock.Device_Inserttime.desc()).paginate(int(page), int(size), False)
        l = []
        rs_data = {
            'total_page': res.pages,
            'datalist': '',
            'total': res.total
        }
        l = []
        for i in res.items:
            l.append({'imei': i.Device_IMEI, 'sales_name': i.Sales_Name, 'company_name': i.Company_Name,
                      'sales_time': str(i.Sales_Time).split('.')[0],
                      'Flow_Fee_Start_Time': str(i.Flow_Fee_Start_Time).split('.')[0],
                      'Flow_Fee_End_Time': str(i.Flow_Fee_End_Time).split('.')[0], 'sales_status': i.Sales_Statues})
        rs_data['datalist'] = l
        return rs_data

    def search_my_stock(self, is_disable):
        res = db.session.query(DeviceStock).filter(DeviceStock.is_disable == is_disable)
        if 'company' in self.data.keys():
            company = self.data['company']
            res = res.filter(DeviceStock.Company_Name.like('%' + company + '%'))
        if 'imei' in self.data.keys():
            imei = self.data['imei']
            res = res.filter(DeviceStock.Device_IMEI.like('%' + imei + '%'))
        if 'sales_name' in self.data.keys():
            sales_name = self.data['sales_name']
            res = res.filter(DeviceStock.Sales_Name.like('%' + sales_name + '%'))
        return res

    def close_conn(self):
        db.session.close()
# data = [{"imei": 351608086043218, "user_name": "admin", "id": "84"},
#         {"imei": 351608086043283, "user_name": "admin", "id": "84"},
#         {"imei": 351608086043259, "user_name": "admin", "id": "84"},
#         {"imei": 351608086042285, "user_name": "admin", "id": "84"},
#         {"imei": 351608086041162, "user_name": "admin", "id": "84"},
#         {"imei": 351608086043085, "user_name": "admin", "id": "84"},
#         {"imei": 351608086037301, "user_name": "admin", "id": "84"}]
#

# print(b)
# data = {"page": 1, "size": 20, "id": "84", "imei": "351608086050478"}
# s = device_stock(data, ip='192.168.1.1')
# b = s.get_all_stock()
# print(b)
