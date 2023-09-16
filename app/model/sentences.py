
from sqlalchemy.sql import func
from app import db


class sentences(db.Model):
    __tablename__="sentences"
    
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    sep = db.Column(db.String(30, collation='utf8mb4_unicode_ci'))
    sentence = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    create_date = db.Column(db.DateTime, default=func.now())
    update_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, sep, sentence, create_date, update_date):
        self.sep = sep
        self.sentence = sentence
        self.create_date = create_date
        self.update_date = update_date
        