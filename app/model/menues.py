
from sqlalchemy.sql import func
from app import db


class menues(db.Model):
    __tablename__="menues"
    
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    sep = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    menu = db.Column(db.String(300, collation='utf8mb4_unicode_ci'))
    create_date = db.Column(db.DateTime, default=func.now())
    update_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, sep, menu, create_date, update_date):
        self.sep = sep
        self.menu = menu
        self.create_date = create_date
        self.update_date = update_date
        