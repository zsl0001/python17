import sys

sys.path.append("..")
from datetime import datetime, timedelta
from time import sleep

from sqlalchemy import or_, and_

from models import db
from my_db.my_models import m_set
from models import Salesarea, User, TMSSale, TMSDevice, get_no_company_sales, get_all_id
from my_db import Models

l = []


# a = get_all_id(1)

def find_all_tree(parent_id):
    m = []
    r = db.session.query(Salesarea).filter(Salesarea.parent_id.in_(parent_id)).all()
    for i in r:
        l.append(i.area_id)
        m.append(i.area_id)
    if len(m) != 0:
        return find_all_tree(parent_id=m)
    else:
        return l


class sales_company_info:
    def __init__(self, data):
        self.data = data
        self.area_id = [data['area_id']]

    def get_company_list(self):
        r_data = {
            'count': '',
            'datalist': '',
            'no_company': ''
        }
        b_data = {
            "Bind_Company": '',
            "Sales_Company": '',
            "Sales_name": '',
            "creat_time": '',
            "disable": '',
            "last_login_time": '',
            "user_id": '',
            "username": ""
        }
        all_tree = find_all_tree(self.area_id)
        m = []
        r_data['no_company'] = get_no_company_sales()
        if 'user_id' in self.data.keys():
            r = db.session.query(User, Salesarea).filter(User.id == TMSSale.user_id,
                                                         TMSSale.user_id == self.data['user_id'],
                                                         User.is_disable == 0,
                                                         User.parent_id.in_(all_tree + self.area_id),
                                                         TMSSale.Is_disabled == 0,
                                                         Salesarea.area_id.in_(all_tree + self.area_id)).order_by(
                User.join_time).all()[(self.data['page'] - 1) * self.data['size']:self.data['page'] * self.data['size']]
            r1 = db.session.query(User, Salesarea).filter(User.id == TMSSale.user_id,
                                                          User.is_disable == 0,
                                                          TMSSale.user_id == self.data['user_id'],
                                                          User.parent_id == Salesarea.area_id,
                                                          TMSSale.Is_disabled == 0,
                                                          ).order_by(
                User.join_time).count()

        else:
            r = db.session.query(User, Salesarea).filter(User.id == TMSSale.user_id,
                                                         User.is_disable == 0,
                                                         User.parent_id == Salesarea.area_id,
                                                         TMSSale.Is_disabled == 0,
                                                         Salesarea.area_id.in_(all_tree + self.area_id)).order_by(
                User.join_time).all()[(self.data['page'] - 1) * self.data['size']:self.data['page'] * self.data['size']]
            r1 = db.session.query(User).filter(User.is_disable == 0,
                                               User.parent_id.in_(all_tree + self.area_id),
                                               ).order_by(User.join_time).count()
        for i in r:
            l = []
            b_data['Sales_Company'] = i.Salesarea.area_name
            b_data['Sales_name'] = i.User.sales_name
            b_data['creat_time'] = i.User.join_time.split('.')[0]
            b_data['disable'] = i.User.is_disable
            b_data['last_login_time'] = i.User.last_seen.split('.')[0]
            b_data['user_id'] = i.User.id
            b_data['username'] = i.User.username
            if 'user_id' in self.data.keys():
                company = db.session.query(TMSSale).filter(TMSSale.user_id == i.User.id, TMSSale.Is_disabled == 0,
                                                           TMSSale.user_id == self.data['user_id']).all()
            else:
                company = db.session.query(TMSSale).filter(TMSSale.user_id == i.User.id, TMSSale.Is_disabled == 0).all()
            for k in company:
                l.append(
                    {"Company_name": k.Company_Name, "Bind_time": k.Bind_time.split('.')[0], 'Company_ID': k.Company_Id,
                     'Contacts': k.Contacts})
            rc = [{'count': len(l), 'datalist': l}]
            b_data['Bind_Company'] = rc
            m.append(b_data.copy())
        r_data['datalist'] = m
        r_data['count'] = r1
        all_tree.clear()
        return r_data


def sales_company(args):
    return sales_company_info(data=args)


# data = {
#     'area_id': 10001,
#     'page': 1,
#     'size': 10,
#     'id': "84"
# }
# s = sales_company_info(data=data)
# print(s.get_company_list())
