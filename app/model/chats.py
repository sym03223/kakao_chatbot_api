
from sqlalchemy.sql import func
from app import db


class chats(db.Model):
    __tablename__="chats"
    
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    room = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    sender = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    msg = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    isGroupChat = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime, default=func.now())
    update_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, room, sender, msg, isGroupChat, create_date, update_date):
        self.room = room
        self.sender = sender
        self.msg = msg
        self.isGroupChat = isGroupChat
        self.create_date = create_date
        self.update_date = update_date
        
    def __init__(self, room, sender, msg, isGroupChat):
        self.room = room
        self.sender = sender
        self.msg = msg
        self.isGroupChat = isGroupChat
        
        