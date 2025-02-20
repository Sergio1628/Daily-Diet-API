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
    weight = data.get("weight")
    description = data.get("description")
    diet = data.get("diet")

    if plate_name and description and weight and diet:
        refeicao = Refeicao(plate_name=plate_name, description=description, weight=weight, diet=diet)
        db.session.add(refeicao)
        db.session.commit()
        return jsonify({"mensagem": "Refeição adicionada com sucesso!"})
    
    return jsonify({"mensagem": "Erro!"})
        
@app.route('/refeicao/<int:id_refeicao>', methods=['GET'])
def read_refeicao(id_refeicao):
    refeicao = Refeicao.query.get(id_refeicao)

    if id_refeicao:
        return

if __name__ == '__main__':
    app.run(debug=True)