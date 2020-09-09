import sys

sys.path.append("..")
from datetime import datetime, timedelta
from time import sleep

from sqlalchemy import or_, and_

from models import db
from my_db.my_models import m_set
from models import Salesarea, User, TMSSale, TMSDevice, TMSCompany
from my_db import Models

global l

l = []


def find_parent(id):
    a = db.session.query(Salesarea).filter(Salesarea.area_id == id, Salesarea.is_disable == 0).first()
    if a:
        if a.parent_id > 0:
            l.append(a.parent_id)
            return find_parent(a.parent_id)
        else:
            return l
    else:
        return []


global M
M = []

count = 0


def find_parent_l2(my_list):
    if len(my_list) > 0:
        global count
        count = count + 1
        i = min(my_list)
        rs = db.session.query(Salesarea).filter(Salesarea.area_id == i).first()
        my_list.remove(i)
        if rs:
            res = {'name': rs.area_name, 'area_id': rs.area_id, 'tree_lv': count}
            M.append(res)
        return find_parent_l2(my_list)
    else:
        return M


# l = [10001, 1, 1000110011]
# print(find_parent_l2(l))
global manager_list

all_list = []


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
    child = db.session.query(Salesarea).filter(Salesarea.parent_id == id, Salesarea.is_disable == 0).all()
    if len(child) != 0:
        for i in child:
            l_list = l_list + get_child(i.area_id)
        return find_all_child(i.area_id)
    else:
        for k in child:
            l_list = l_list + get_child(k.area_id)
        return l_list


#
# a = find_all_child(10001)
# print(a)


class Search_sales_tree:
    def __init__(self, data):
        self.data = data
        self.id = [data['id']]
        if 'sales_name' in data.keys():
            self.data['sales_name'] = data['sales_name']
        if 'company_name' in data.keys():
            self.data['company_name'] = data['company_name']
        if 'IMEI' in data.keys():
            self.data['IMEI'] = data['IMEI']

    def get_id_by_sales_name(self):
        my_list = []
        role_id = db.session.query(User).filter(User.id == self.id, User.is_disable == 0).first()
        try:
            if role_id.role_id == 1:
                re = db.session.query(User).filter(User.sales_name.like('%' + self.data['sales_name'] + '%'),
                                                   User.is_disable == 0).all()
            elif role_id.is_manager == 1:
                re = db.session.query(User).filter(User.sales_name.like('%' + self.data['sales_name'] + '%'),
                                                   User.is_disable == 0, User.id == self.id,
                                                   User.parent_id == role_id.top_parent_id).all()
            else:
                re = db.session.query(User).filter(User.sales_name.like('%' + self.data['sales_name'] + '%'),
                                                   User.is_disable == 0, User.id == self.id).all()
            my_rslist = []
            for i in re:
                m = []
                a = find_parent(i.parent_id)
                m = m + a
                m.append(i.parent_id)
                my_list.append({'user_id': i.id, 'area_list': list(set(m)), 'sales_name': i.sales_name})
            for k in my_list:
                global count
                global M
                my_rslist.append(find_parent_l2(k['area_list']))
                my_rslist = my_rslist + [{'user_id': i.id, 'sales_name': i.sales_name, 'tree_lv': count + 1}]
                M = []
                count = 0
            db.session.close()
            return my_rslist
        except:
            db.session.close()
            return {'res': '参数错误', 'code': -100001}

    # def get_id_by_area_name(self):
    #     role_id = db.session.query(User).filter(User.id == self.id, User.is_disable == 0).first()
    #     re = db.session.query(Salesarea).filter(Salesarea.area_name.like('%' + self.data['area_name'] + '%'),
    #                                             Salesarea.is_disable == 0).all()
    #     r_id = []
    #     my_rslist = []
    #     if role_id.role_id == 1:
    #         p_id = db.session.query(Salesarea).filter(Salesarea.is_disable == 0).all()
    #         for id in p_id:
    #             r_id.append(id.are_id)
    #     else:
    #         p_id = role_id.parent_id
    #         r_id = find_parent(p_id)
    #         r_id.append(role_id.parent_id)
    #     for i in re:
    #         if i.parent_id in r_id:
    #             m = []
    #             a = find_parent(i.parent_id)
    #             m = m + a
    #             if i.parent_id > 0:
    #                 m.append(i.parent_id)
    #                 global count
    #                 global M
    #                 my_rslist.append(find_parent_l2(list(set(m))))
    #                 ##  + [{'area_id': i.area_id, 'area_name': i.area_name, 'tree_lv': count + 1}]
    #                 count = 0
    #                 M = []
    #     print(my_rslist)
    #     # return my_rslist
    #     # except:
    #     #     return {'res': '参数错误', 'code': -100001}

    def get_id_by_imei(self):
        role_id = db.session.query(User).filter(User.id == self.id, User.is_disable == 0).first()
        if role_id.role_id == 1:
            dev_company_id = db.session.query(TMSDevice, TMSCompany).filter(TMSDevice.Device_Invalid == 0,
                                                                            TMSCompany.Company_ID == TMSDevice.Device_CompanyID,
                                                                            TMSSale.Is_disabled == 0,
                                                                            or_(TMSDevice.Device_Type == 3,
                                                                                TMSDevice.Device_Type == 2),
                                                                            TMSDevice.Device_IMEICode.like(
                                                                                '%' + self.data[
                                                                                    'IMEI'] + '%'))
            rs = db.session.query(User).filter(User.is_disable == 0, User.id != self.data['id']).all()
            self.id = [i.id for i in rs]
        elif role_id.is_manager == 1:
            area_p_id = db.session.query(Salesarea).filter(Salesarea.area_id == role_id.parent_id).first()
            all_child = find_all_child(area_p_id.parent_id) + [area_p_id.parent_id]
            all_child = list(set(all_child))
            u_id = []
            for i in all_child:
                r = db.session.query(User).filter(User.parent_id == i).all()
                for k in r:
                    u_id.append(k.id)
            self.id = u_id
            dev_company_id = db.session.query(TMSDevice, TMSCompany, User).filter(TMSDevice.Device_Invalid == 0,
                                                                                  TMSCompany.Company_ID == TMSDevice.Device_CompanyID,
                                                                                  TMSSale.Is_disabled == 0,
                                                                                  User.is_disable == 0,
                                                                                  User.id.in_(self.id),
                                                                                  or_(TMSDevice.Device_Type == 3,
                                                                                      TMSDevice.Device_Type == 2),
                                                                                  TMSDevice.Device_IMEICode.like(
                                                                                      '%' + self.data[
                                                                                          'IMEI'] + '%'))
        else:
            dev_company_id = db.session.query(TMSDevice, TMSCompany, User).filter(TMSDevice.Device_Invalid == 0,
                                                                                  TMSCompany.Company_ID == TMSDevice.Device_CompanyID,
                                                                                  TMSSale.Is_disabled == 0,
                                                                                  User.is_disable == 0,
                                                                                  User.id.in_(self.id),
                                                                                  or_(TMSDevice.Device_Type == 3,
                                                                                      TMSDevice.Device_Type == 2),
                                                                                  TMSDevice.Device_IMEICode.like(
                                                                                      '%' + self.data[
                                                                                          'IMEI'] + '%'))
        d_l = []
        for i in dev_company_id.all():
            d_l.append(
                {'company_id': i.TMSCompany.Company_ID, 'company_name': i.TMSCompany.Company_Name, 'datalist': ''})
        seen = set()
        new_l = []
        for d in d_l:  # 字典去重
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        my_rslist = []
        for v in new_l:
            de_l = []
            dev_data = db.session.query(TMSDevice).filter(TMSDevice.Device_Invalid == 0, or_(TMSDevice.Device_Type == 3,
                                                                                             TMSDevice.Device_Type == 2),
                                                          TMSDevice.Device_CompanyID == v['company_id'],
                                                          User.id.in_(self.id),
                                                          TMSDevice.Device_IMEICode.like(
                                                              '%' + self.data['IMEI'] + '%')).all()
            # dev_company_id.filter(TMSDevice.Device_CompanyID == v['company_id']).all()
            for dev in dev_data:
                de_l.append({'IMEI': dev.Device_IMEICode})
            v['datalist'] = de_l
            parent_id = db.session.query(TMSSale, User, Salesarea).filter(User.id == TMSSale.user_id,
                                                                          User.is_disable == 0,
                                                                          User.id.in_(self.id),
                                                                          TMSSale.Is_disabled == 0,
                                                                          TMSSale.Company_Id == v[
                                                                              'company_id']).first()
            if parent_id is not None:
                m = []
                a = find_parent(parent_id.User.parent_id)
                m = m + a
                m.append(parent_id.User.parent_id)
                my_list = []
                if parent_id.User.parent_id > 0:
                    m.append(parent_id.User.parent_id)
                    global count
                    global M
                    a = find_parent_l2(list(set(m)))
                    my_list.append({'user_id': parent_id.User.id, 'parent_id': parent_id.User.parent_id,
                                    'sales_name': parent_id.User.sales_name, 'datalist': v, 'tree_lv': count + 1})
                    my_rslist.append(a + my_list)
                    count = 0
                    M = []
        db.session.close()
        return my_rslist
        # except:
        #     return {'res': '参数错误', 'code': -100001}

    def data_control(self):
        if 'sales_name' in self.data.keys():
            return self.get_id_by_sales_name()
        if 'company_name' in self.data.keys():
            return self.get_company_id()
        if 'IMEI' in self.data.keys():
            return self.get_id_by_imei()

    def find_company(self, re1):
        r_list = []
        s_id_list = []
        for s_id in re1:
            s_id_list.append(s_id.TMSSale.user_id)
        s_id_list = list(set(s_id_list))
        # 根据用户ID获取公司信息
        for u_id in s_id_list:
            global M
            M = []
            my_rslist = []
            company_list = []  # 保存对应销售的公司列表
            re = db.session.query(User, TMSSale).filter(User.id == u_id, TMSSale.Is_disabled == 0,
                                                        TMSSale.Company_Name.like(
                                                            '%' + self.data['company_name'] + '%'),
                                                        User.id == TMSSale.user_id, User.is_disable == 0).all()
            for i in re:
                my_list = []
                total = db.session.query(TMSDevice).filter(TMSDevice.Device_Invalid == 0,
                                                           TMSDevice.Device_CompanyID == i.TMSSale.Company_Id,
                                                           or_(TMSDevice.Device_Type == 3,
                                                               TMSDevice.Device_Type == 2))
                imei_list = [i.Device_IMEICode for i in total.all()]
                company_list.append(
                    {'company_name': i.TMSSale.Company_Name, 'company_id': i.TMSSale.Company_Id, 'count': total.count(),'datalist':imei_list})
            m = []
            p_id = db.session.query(User).filter(User.is_disable == 0, User.id == u_id).first()
            a = find_parent(p_id.parent_id)
            m = m + a
            a.clear()
            m.append(p_id.parent_id)
            my_list.append({'user_id': u_id, 'area_list': list(set(m))})
            for k in my_list:
                global count
                my_rslist.append(find_parent_l2(k['area_list']) + [
                    {'sales_name': p_id.sales_name, 'user_id': p_id.id, 'datalist': company_list,
                     'tree_lv': count + 1}])
                M = []
                count = 0
            r_list.append(my_rslist)
        db.session.close()
        return r_list

    def get_company_id(self):  # 按照公司搜索
        role_id = db.session.query(User).filter(User.id == self.id, User.is_disable == 0).first()
        if role_id.role_id == 1:  # 管理员搜索
            re1 = db.session.query(TMSSale, User).filter(
                TMSSale.Company_Name.like('%' + self.data['company_name'] + '%'),
                TMSSale.Is_disabled == 0, User.id == TMSSale.user_id, User.is_disable == 0).all()
            d = self.find_company(re1)
        if role_id.is_manager == 1:  # 经理搜索
            area_p_id = db.session.query(Salesarea).filter(Salesarea.area_id == role_id.parent_id).first()
            all_child = find_all_child(area_p_id.parent_id) + [area_p_id.parent_id]
            all_child = list(set(all_child))
            re1 = db.session.query(TMSSale, User).filter(
                TMSSale.Company_Name.like('%' + self.data['company_name'] + '%'),
                TMSSale.Is_disabled == 0, User.id == TMSSale.user_id, User.is_disable == 0,
                User.parent_id.in_(all_child)).all()
            d = self.find_company(re1)
        if role_id.is_manager == 0 and role_id.role_id == 0:  # 销售搜索
            re1 = db.session.query(TMSSale, User).filter(
                TMSSale.Company_Name.like('%' + self.data['company_name'] + '%'),
                TMSSale.Is_disabled == 0, User.id == TMSSale.user_id, User.is_disable == 0,
                User.parent_id == role_id.parent_id, User.id == self.data['id']).all()
            d = self.find_company(re1)
        db.session.close()
        return d

    def search_company_name(self):
        role_id = db.session.query(User).filter(User.id == self.id, User.is_disable == 0).first()
        if role_id.role_id == 1:  # 管理员搜索
            re1 = db.session.query(TMSSale, User).filter(
                TMSSale.Company_Name.like('%' + self.data['company_name'] + '%'),
                TMSSale.Is_disabled == 0, User.id == TMSSale.user_id, User.is_disable == 0).all()
        if role_id.is_manager == 1:  # 经理搜索
            area_p_id = db.session.query(Salesarea).filter(Salesarea.area_id == role_id.parent_id).first()
            all_child = find_all_child(area_p_id.parent_id) + [area_p_id.parent_id]
            all_child = list(set(all_child))
            re1 = db.session.query(TMSSale, User).filter(
                TMSSale.Company_Name.like('%' + self.data['company_name'] + '%'),
                TMSSale.Is_disabled == 0, User.id == TMSSale.user_id, User.is_disable == 0,
                User.parent_id.in_(all_child)).all()
        if role_id.is_manager == 0 and role_id.role_id == 0:  # 销售搜索
            re1 = db.session.query(TMSSale, User).filter(
                TMSSale.Company_Name.like('%' + self.data['company_name'] + '%'),
                TMSSale.Is_disabled == 0, User.id == TMSSale.user_id, User.is_disable == 0,
                User.parent_id == role_id.parent_id, User.id == self.data['id']).all()
        db.session.close()
        s_id_list = []
        for s_id in re1:
            s_id_list.append(s_id.TMSSale.user_id)
        s_id_list = list(set(s_id_list))
        cp_name = db.session.query(TMSSale).filter(TMSSale.user_id.in_(s_id_list), TMSSale.Is_disabled == 0,TMSSale.Company_Name.like('%' + self.data['company_name'] + '%')).all()
        cp_name_list = [i.Company_Name for i in cp_name]
        return cp_name_list

# data = {'company_name': "山东", 'id': "84"}
# s = Search_sales_tree(data)
# # #
# a = s.search_company_name()
# print(a)
# for i in a:
#     print(i)

# a = find_all_child(10001)
# b = list(set(a))
# print(b)
# print(len(b))
