
from sqlalchemy.sql import func
from app import db


class enhancement_guiness(db.Model):
    __tablename__="enhancement_guiness"
    
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    item_name = db.Column(db.String(300,collation='utf8mb4_unicode_ci'))
    item_level = db.Column(db.Integer, default=0)
    room = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    create_date = db.Column(db.DateTime, default=func.now())
    update_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, user, item_name, item_level, room, create_date, update_date):
        self.user = user
        self.item_name = item_name
        self.item_level = item_level
        self.room = room
        self.create_date = create_date
        self.update_date = update_date
        
    def __init__(self, user, item_name, item_level, room):
        self.user = user
        self.item_name = item_name
        self.item_level = item_level
        self.room = room