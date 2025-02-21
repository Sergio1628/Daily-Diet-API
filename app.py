from flask import Flask, jsonify, request
from database import db
from models.refeicao import Refeicao
from datetime import datetime

#SQLAlchemy
app = Flask(__name__)
app.config["SECRET_KEY"]= "your secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/DailyDiet'

db.init_app(app)

VALID_FIELDS = {"plate_name", "weight", "description", "diet"}

# Create
@app.route('/refeicao', methods=['POST'])
def create_refeicao():
    data = request.json
    plate_name = data.get("plate_name")
    weight = data.get("weight")
    description = data.get("description")
    diet = data.get("diet")
    refeicao = [plate_name, description, weight]

    if all (refeicao) and diet is not None:
        refeicao = Refeicao(plate_name=plate_name, description=description, weight=weight, diet=diet)
        db.session.add(refeicao)
        db.session.commit()
        return jsonify({"mensagem": "Refeição adicionada com sucesso!"})
    
    return jsonify({"mensagem": "Erro!"})
        
@app.route('/refeicao/<int:id_refeicao>', methods=['GET'])
def read_refeicao(id_refeicao):
    refeicao = Refeicao.query.get(id_refeicao)

    if refeicao:
        return {"plate_name": refeicao.plate_name}

    return jsonify({"mensagem": "Refeição não encontrada!"}), 404


@app.route('/refeicao/<int:id_refeicao>', methods=['PATCH'])
def update_refeicao(id_refeicao):
    data = request.json
    refeicao = Refeicao.query.get(id_refeicao)
    
    # Valida se o id da refeiçao existe
    if not refeicao:
        return jsonify({"mensagem": "Erro! Refeição não encontrada."}), 404 
    # Valida se pelo menos um dos campos validos existe na requisição
    if not any(key in data for key in VALID_FIELDS):
        return jsonify({"mensagem": "Nenhum dado válido enviado."}), 400

    # Percorre todos os campos válidos e substitui dinamicamente com os novos dados
    for field in VALID_FIELDS:
        if field in data:
            setattr(refeicao, field, data[field])

    db.session.commit()

    return jsonify ({"mensagem": f"Refeição {id_refeicao} atualizada com sucesso!"})
    
           


''' Bloco funcional, mas como PUT, que exige todos os parametros da var refeicao no payload
    if refeicao:
        refeicao.plate_name = data.get("plate_name")
        refeicao.weight = data.get("weight")
        refeicao.description = data.get("description")
        refeicao.diet = data.get("diet")
        
        db.session.commit()'''

if __name__ == '__main__':
    app.run(debug=True)