import json
import sys

sys.path.append("..")
from datetime import datetime
from models import db
from sqlalchemy import and_, or_


class APIInforMession(db.Model):
    __tablename__ = 'API_InforMession '
    __table_args__ = {'schema': 'WLY.dbo'}
    Info_Id = db.Column(db.BigInteger, nullable=False, index=True, primary_key=True)
    Info_Address = db.Column(db.String(128))
    Info_Longitude = db.Column(db.String(128))
    Info_Latitude = db.Column(db.String(128))
    Info_Invalid = db.Column(db.Integer, default=0)
    Inform_CreateTime = db.Column(db.DateTime, default=datetime.now)

