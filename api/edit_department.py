import sys

sys.path.append("..")
from models import db
from models import Salesarea, User, TMSSale, TMSDevice


class Edit_deppart:
    def __init__(self, data=None):
        self.data = data

    def get_department(self):
        l = []
        if self.data is None or len(self.data)==0:
            res = db.session.query(Salesarea).filter(Salesarea.parent_id == 0).all()
            for i in res:
                l.append({'area_id': i.parent_id, 'area_name': i.area_name})
        else:
            res = db.session.query(Salesarea).filter(Salesarea.parent_id == self.data['parent_id']).all()
            for i in res:
                l.append({'area_id': i.parent_id, 'area_name': i.area_name})
        return l

    def add_department(self):
        res = Salesarea()
        if 'is_manager' in self.data.keys():
            res.is_manager = self.data['is_manager']
            max_manager_id = db.session.query(Salesarea).filter(Salesarea.parent_id == self.data['parent_id'],
                                                                Salesarea.is_manager == 1).order_by(
                -Salesarea.area_id).first()
            if max_manager_id is None:
                res.area_id = int(str(self.data['parent_id']) + '1001' + '1')
            else:
                res.area_id = max_manager_id.area_id + 1
        else:
            max_manager_id = db.session.query(Salesarea).filter(Salesarea.parent_id == self.data['parent_id'],
                                                                Salesarea.is_manager == 0).order_by(
                -Salesarea.area_id).first()
            if max_manager_id is None:
                res.area_id = int(str(self.data['parent_id']) + '0001')
            else:
                res.area_id = max_manager_id.area_id + 1
        res.area_name = self.data['area_name']
        res.parent_id = self.data['parent_id']
        res.top_parent_id = self.data['top_parent_id']
        res.is_disable = self.data['is_disable']

        try:
            db.session.add(res)
            db.session.commit()
            return {'res': '新增成功!','code':1001}
        except:
            return {'res': '新增失败!','code':-1001}

    def data_control(self):
        if 'parent_id' in self.data.keys() and len(self.data.keys())==1:
            return self.get_department()
        elif self.data is None or len(self.data) ==0:
            return self.get_department()
        else:
            return self.add_department()

# data = {
#     'parent_id': 10002,
# }
#
# a = Edit_deppart(data)
# print(a.data_control())
