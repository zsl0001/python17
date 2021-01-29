import sys

sys.path.append("..")
import models
from my_db import Models
from models import app, db, User, TMSSale, CPUser
from my_db.my_sql import open_mysql
from my_db.my_mgdb import my_mog
from my_db.my_models import My_Models
from api.login_mode.response_code import RET
from api.set_name import Set_Name, get_ln, get_ln2
from api.sales_tree import sales_tree
from api.edit_department import Edit_deppart
from api.get_sales_company_info import sales_company
from api.search_sales_tree import Search_sales_tree
from api.get_more_postion import More_Position
from api.device_stock import device_stock
from api.login_mode.validatecode import VercCode
from api.login_mode.pic.cutimg import getAuthImage, AuthImage, get_redis_res
from api.bind_company import Set_Device_Comapy
from api.top_order import get_top_order_info
from api.get_all_device import get_all_device
from api.get_device_info import my_info
from api.search_pactcode import search_pactcode_by_imei2
from api.tms_register import *
from api.third_temp import *
# a = db.session.query(User).filter(User.username =='admin').first()
# print(a.username)
# a = open_mysql()
