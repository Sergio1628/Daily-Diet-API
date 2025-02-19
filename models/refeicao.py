from database import db
from datetime import datetime


class Refeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_refeicao = db.Column(db.String(40), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, default=datetime) 
    Is_diet = db.Column(db.Boolean(), nullable=False)