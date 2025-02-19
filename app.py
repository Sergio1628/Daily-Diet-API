from flask import Flask, jsonify, request
from database import db
from models.refeicao import Refeicao
from datetime import datetime

#SQLAlchemy
app = Flask(__name__)
app.config["SECRET_KEY"]= "your secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/DailyDiet'

db.init_app(app)

# Create
@app.route('/refeicao', methods=['POST'])
def create_refeicao():
    data = request.json
    plate_name = data.get("plate_name")
    description = data.get("description")
    weight = data.get("weight")
    diet =data.get("diet")
    date = datetime

    if plate_name and description and weight and diet and date:
        refeicao = Refeicao(nome_refeicao=plate_name, description=description, weight=weight, diet=diet, date=date)
        db.session.add(refeicao)
        db.session.commit()
        

if __name__ == '__main__':
    app.run(debug=True)