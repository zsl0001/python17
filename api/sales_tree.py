import sys

sys.path.append("..")
from sqlalchemy import or_, and_

from models import db
from my_db.my_models import m_set
from models import Salesarea, User, TMSSale, TMSDevice
from my_db import Models

global l
l = []


def find_parent(id):
    a = db.session.query(Salesarea).filter(Salesarea.area_id == id).first()
    if a.parent_id > 0:
        l.append(a.parent_id)
        return find_parent(a.parent_id)
    else:
        return l


def find_all_parent_id(id):
    rs = db.session.query(User).filter(User.id == id, User.is_disable == 0).first()
    my_list = find_parent(rs.parent_id)
    my_list.append(rs.parent_id)
    global l
    l = []
    return my_list


'''
最上层节点为1-9个数
子节点编号为1000+上层节点，例如：上层节点编号为1，改层为'1000' + '1' 为10001
经理编号为 改层节点数据+1，例如：改层节点编号为10001，改层为'10001' + '1' 100011
'''


class sales_tree:
    def __init__(self, data):
        self.data = data
        self.data['id'] = int(data['id'])
        id = db.session.query(User).filter(User.id == int(data['id']), User.is_disable == 0).first()
        if id.role_id:  # 管理员查看所有的数据
            rs = db.session.query(Salesarea).filter(Salesarea.parent_id == 0, Salesarea.is_disable == 0).all()
            self.my_list = [i.area_id for i in rs]
            db.session.close()
        elif id.is_manager:  # 销售经理可以查看公司所有分部门数据
            top = min(find_all_parent_id(int(data['id'])))
            manager_parent_id = db.session.query(User).filter(User.id == int(data['id']), User.is_manager == 1).first()
            manager_Salesarea_parent_id = db.session.query(Salesarea).filter(
                Salesarea.area_id == manager_parent_id.parent_id, Salesarea.is_disable == 0).first()
            all = list(set(find_all_parent_id(int(data['id']))))
            rs = db.session.query(Salesarea).filter(Salesarea.parent_id == manager_Salesarea_parent_id.parent_id,
                                                    Salesarea.is_disable == 0).all()
            self.my_list = [i.area_id for i in rs]
            self.my_list = list(set(all + self.my_list))
            db.session.close()
        else:  # 销售只能查看自己的公司数据
            self.my_list = set(find_all_parent_id(int(data['id'])))

    def get_top_tree(self):  # 根据用户id,获取最上层节点
        return min(self.my_list)

    def get_first_children_tree(self):  # 控制台第一次请求时返回的子节点
        id = db.session.query(User).filter(User.id == self.data['id'], User.is_disable == 0).first()
        res = {'count': '', 'datalist': ''}
        l = []
        if id.role_id:
            children = db.session.query(Salesarea).filter(Salesarea.parent_id == 0).all()
        else:
            children = db.session.query(Salesarea).filter(Salesarea.area_id == self.get_top_tree()).all()
        for i in children:
            l.append({'area_id': i.area_id, 'area_name': i.area_name, 'next_node': True})
        res['count'] = len(l)
        res['datalist'] = l
        return res

    def get_next_children_tree(self):  # 获取下一级子节点
        id = db.session.query(User).filter(User.id == self.data['id'], User.is_disable == 0).first()
        top_id = db.session.query(Salesarea).filter(Salesarea.parent_id == 0,Salesarea.is_disable ==0).all()
        if id.is_manager==1:
            # 获取经理权限的区域ID
            m_top_id = db.session.query(Salesarea).filter(Salesarea.area_id == id.parent_id,Salesarea.is_disable ==0).first()
        else:
            # 获取销售权限的区域ID
            m_top_id = db.session.query(Salesarea).filter(Salesarea.area_id == 1000310011,Salesarea.is_disable == 0).first()
        top_list = [i.area_id for i in top_id]
        res = {'count': '', 'datalist': ''}
        l = []
        if id.role_id:
            u_area_id = db.session.query(Salesarea).filter(Salesarea.area_id == id.parent_id,
                                                           Salesarea.is_disable == 0).first()
            children = db.session.query(Salesarea).filter(Salesarea.parent_id == self.data['area_id']).all()
        elif id.parent_id in top_list or m_top_id.parent_id in top_list:
            u_area_id = db.session.query(Salesarea).filter(Salesarea.area_id == id.parent_id,
                                                           Salesarea.is_disable == 0).first()
            children = db.session.query(Salesarea).filter(Salesarea.parent_id == self.data['area_id']).all()
        else:
            u_area_id = id
            children = db.session.query(Salesarea).filter(Salesarea.parent_id == self.data['area_id'],
                                                          Salesarea.area_id.in_(self.my_list)).all()
        if len(children) == 0:
            if id.role_id == 1:
                children = db.session.query(User).filter(User.parent_id == self.data['area_id'], User.is_disable == 0).all()
                for i in children:
                    l.append({'area_id': i.parent_id, 'sales_name': i.sales_name, 'user_id': i.id})

                own_data = db.session.query(User).filter(User.parent_id == self.data['area_id'], User.is_disable == 0,
                                                         User.id == self.data['id']).first()
                if own_data is not None:
                    l.append({'area_id': own_data.parent_id, 'sales_name': own_data.sales_name, 'user_id': own_data.id})
            elif u_area_id.parent_id in top_list:
                c_list = [self.data['area_id']]
                children2 = db.session.query(Salesarea).filter(Salesarea.parent_id == self.data['area_id'],
                                                               Salesarea.is_disable == 0).all()
                for k in children2:
                    c_list.append(k.area_id)
                children = db.session.query(User).filter(User.parent_id.in_(c_list), User.is_disable == 0).all()

                for i in children:
                    l.append({'area_id': i.parent_id, 'sales_name': i.sales_name, 'user_id': i.id})
                # own_data = db.session.query(User).filter(User.parent_id == self.data['area_id'], User.is_disable == 0,
                #                                          User.id == self.data['id']).first()
                # if own_data is not None:
                #     l.append({'area_id': own_data.parent_id, 'sales_name': own_data.sales_name, 'user_id': own_data.id})
            elif id.is_manager == 1 and id.role_id == 0 and u_area_id.parent_id not in top_list:
                # p_id = db.session.query(Salesarea).filter(Salesarea.area_id == self.data['area_id']).first()
                children = db.session.query(User).filter(User.id == self.data['id'], User.is_disable == 0).all()
                for i in children:
                    l.append({'area_id': i.parent_id, 'sales_name': i.sales_name, 'user_id': i.id})
                # own_data = db.session.query(User).filter(User.parent_id == self.data['area_id'], User.is_disable == 0,
                #                                          User.id == self.data['id']).first()
                # if own_data is not None:
                #     l.append({'area_id': own_data.parent_id, 'sales_name': own_data.sales_name, 'user_id': own_data.id})

            else:
                children = db.session.query(User).filter(User.parent_id == self.data['area_id'],
                                                         User.is_disable == 0,User.id ==self.data['id']).all()
                for i in children:
                    l.append({'area_id': i.parent_id, 'sales_name': i.sales_name, 'user_id': i.id})

                # own_data = db.session.query(User).filter(User.parent_id == self.data['area_id'], User.is_disable == 0,
                #                                          User.id == self.data['id']).first()
                # if own_data is not None:
                #     l.append({'area_id': own_data.parent_id, 'sales_name': own_data.sales_name, 'user_id': own_data.id})
        else:
            for i in children:
                count = db.session.query(Salesarea).filter(Salesarea.parent_id == i.area_id).count()
                count1 = db.session.query(User).filter(User.parent_id == i.area_id, User.is_disable == 0).count()
                if count != 0 or count1 != 0:
                    l.append({'area_id': i.area_id, 'area_name': i.area_name, 'next_node': True})
                else:
                    l.append({'area_id': i.area_id, 'area_name': i.area_name, 'next_node': False})
                count2 = db.session.query(User).filter(User.parent_id == self.data['area_id'], User.is_disable == 0)
                if count2.count() != 0:
                    for k in count2:
                        l.append(
                            {'area_id': i.parent_id, 'sales_name': k.sales_name, 'next_node': False, 'user_id': k.id})
        res['count'] = len(l)
        res['datalist'] = l
        db.session.close()
        return res

    def get_company_devices(self):  # 获取公司列表和设备码
        res = {'count': '', 'datalist': ''}
        l = []
        res_data = db.session.query(TMSSale).filter(TMSSale.Is_disabled == 0,
                                                    TMSSale.user_id == self.data['user_id']).all()
        for i in res_data:
            IMEI_list = []
            dev_list = db.session.query(TMSDevice).filter(
                and_(or_(TMSDevice.Device_Type == 3, TMSDevice.Device_Type == 2),
                     TMSDevice.Device_Invalid == 0, TMSDevice.Device_CompanyID == i.Company_Id)).all()
            for k in dev_list:
                IMEI_list.append({'Devices': k.Device_IMEICode})
            l.append({'Company_Name': i.Company_Name, 'Company_Id': i.Company_Id, 'IMEI': IMEI_list,
                      'Total': len(IMEI_list)})
        res['count'] = len(l)
        res['datalist'] = l
        db.session.close()
        return res

    def data_control(self):
        print(self.data)
        if 'user_id' in self.data.keys():

            return self.get_company_devices()
        elif 'id' in self.data.keys() and len(self.data.keys()) == 3:

            return self.get_first_children_tree()
        else:

            return self.get_next_children_tree()


#  id  24 self.data.keys()部门经理  31 总经理  北京 33普通销售
#  id 43 上海市场部
# data = {'id': 24, "area_id": 10001}
# {"label":"北京市场三部","area_id":10003,"id":"23"}
# data = {"area_id":10002,"id":"23"}
# data = {'area_id': 10002, 'sales_name': '范若若', 'user_id': 29,'id':'23'}
# sales_tree = sales_tree(data)
# print(sales_tree.data_control())area_id

# data = {
#     "area_id": 1,
#     "id": "105"
# }
# sales_tree1 = sales_tree(data)
# print(sales_tree1.data_control())
