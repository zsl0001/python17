import sys

sys.path.append("..")
from models import db

from models import Salesarea, User, TMSSale, TMSDevice, TMSCompany


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
    my_l =[]
    if u_id.is_manager ==1:
        id = u_id.parent_id
        p_id = db.session.query(Salesarea).filter(Salesarea.is_disable == 0, Salesarea.area_id==id).first()
        l = find_all_child(p_id.parent_id)
        for area in l:
            rs = db.session.query(User).filter(User.is_disable == 0, User.parent_id==area).all()
            if rs:
                for k in rs:
                    my_l.append(k.id)
    else:
        my_l.append(id)
    return my_l



