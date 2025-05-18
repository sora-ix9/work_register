from app import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON

class Work_register_tb(db.Model):
    __table_name__ = 'Work_register_tb'

    registry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    officer_id = db.Column(db.String)
    full_name = db.Column(db.String)
    registry_img = db.Column(db.LargeBinary)
    registry_time = db.Column(db.String)

    # def __init__(self, registry_id, officer_id, full_name, registry_img, registry_time):
    def __init__(self, registry_img, registry_time):
        
        # self.registry_id = registry_id
        # self.officer_id = officer_id
        # self.full_name = full_name
        self.registry_img = registry_img
        self.registry_time = registry_time

    def __repr__(self):
        return f'id = {self.id}'