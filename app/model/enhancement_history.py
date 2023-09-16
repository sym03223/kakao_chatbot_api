
from sqlalchemy.sql import func
from app import db


class enhancement_history(db.Model):
    __tablename__="enhancement_history"
    
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    item_name = db.Column(db.String(300,collation='utf8mb4_unicode_ci'))
    room = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    before_level = db.Column(db.Integer)
    change_level = db.Column(db.Integer)
    current_level = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=func.now())
    update_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, user, item_name, room, before_level, change_level, current_level, create_date, update_date):
        self.user = user
        self.item_name = item_name
        self.room = room
        self.before_level = before_level
        self.change_level = change_level
        self.current_level = current_level
        self.create_date = create_date
        self.update_date = update_date
    
    def __init__(self, user, item_name, room, before_level, change_level, current_level):
        self.user = user
        self.item_name = item_name
        self.room = room
        self.before_level = before_level
        self.change_level = change_level
        self.current_level = current_level