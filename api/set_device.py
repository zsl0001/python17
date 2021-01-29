import sys
import datetime

sys.path.append("..")
# from datetime import datetime, timedelta

from sqlalchemy import extract, or_

from models import db, DeviceStock, TemperatureReceipt

res2 = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI.like('351608087%')).with_for_update(read=True).all()
print(len(res2))
# res3 = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI.like('351608086%')).with_for_update(read=True).all()
for i in res2:
    i.Device_type = '2'
    i.Device_Temperature = '0'
    try:
        print(i.Device_IMEI)
        db.session.commit()
    except Exception as e:
        print(e)

# l = ['351608086051054','351608086050981','351608086051245','351608086050585','351608086050429']
# for i in l:
#     k = db.session.query(DeviceStock).filter(DeviceStock.Device_IMEI==i).with_for_update(read=True).first()
#     t = db.session.query(TemperatureReceipt).filter(TemperatureReceipt.imei ==i).first()
#     print(t)
#     if t:
#         k.Device_Temperature = '1'
#     else:
#         k.Device_Temperature = '0'
#     try:
#         db.session.commit()
#     except Exception as e:
#         print(e)
