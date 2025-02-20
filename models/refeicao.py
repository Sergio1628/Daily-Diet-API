from database import db
from datetime import datetime


class Refeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_name = db.Column(db.String(40), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    diet = db.Column(db.Boolean, nullable=False, default=False)

#    date = db.Column(db.Date, default=datetime) 