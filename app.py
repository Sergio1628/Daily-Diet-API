from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt
from database import db
from models.refeicao import Refeicao
from models.user import User
from datetime import datetime, timezone

#SQLAlchemy
app = Flask(__name__)
app.config["SECRET_KEY"]= "your secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/DailyDiet'

db.init_app(app)

# Variáveis de login
login_manager = LoginManager()
login_manager.init_app(app)
#view login
login_manager.login_view = 'login'

def is_current_user(user_id):
    if user_id != current_user.id:
        if current_user.role != 'admin':
         return jsonify({'mensagem': 'Erro! Operação não permitida.'}), 403
    return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticação realizada com sucesso!"})

    return jsonify({"message": "Credenciais invalidas"}), 400


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"mensagem:": "Logout realizado com sucesso"})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_passwd = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_passwd, role='user') # especificando a role padrão para facilitar a legibilidade.
        db.session.add(user)
        db.session.commit()
        return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'})

    return jsonify({'mensagem': 'Dados invalidos'}), 400
    

@app.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}
    
    return jsonify({'mensagem': "Usuário não encontrado"}), 404


@app.route('/user/<int:id_user>', methods=['PUT'])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if id_user != current_user.id:
        if current_user.role != 'admin':
            return jsonify({'mensagem': 'Erro! Operação não permitida.'}), 403


    if user and data.get("password"):
        hashed_passwd = bcrypt.hashpw(str.encode(data.get("password")), bcrypt.gensalt())
        user.password = hashed_passwd
        db.session.commit()
        return jsonify({'mensagem': f'Usuário {id_user} atualizado com sucesso'})
    
    
    return jsonify({'mensagem': 'Usuário não encontrado'}), 404

@app.route('/user/<int:id_user>', methods=['DELETE'])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != 'admin':
        return jsonify({'mensagem': 'Operação não permitida!.'}), 403

    if id_user == current_user.id:
        return jsonify({'mensagem': 'Erro! Não é possivel excluir o usuário atual.'}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'mensagem': f'Usuário {id_user} deletado com sucesso!'})
    
    return jsonify({'mensagem': 'Usuário não encontrado'}), 404


@app.route('/hello-world', methods=['GET'])
def hello_world():
    return "Hello World"


VALID_FIELDS = {"plate_name", "weight", "description", "diet", "date"}

# Create
@app.route('/<int:user_id>/refeicao', methods=['POST'])
@login_required
def create_refeicao(user_id):
    error = is_current_user(user_id)

    if error:
        return error

    data = request.json
    plate_name = data.get("plate_name")
    weight = data.get("weight")
    description = data.get("description")
    diet = data.get("diet")
    date = datetime.now(timezone.utc)
    refeicao = [plate_name, description, weight, date]

    if all (refeicao) and diet is not None:
        refeicao = Refeicao(plate_name=plate_name, description=description, weight=weight, diet=diet, user_id=user_id)
        db.session.add(refeicao)
        db.session.commit()
        return jsonify({"mensagem": "Refeição adicionada com sucesso!"})
    
    return jsonify({"mensagem": "Erro!"})


@app.route('/<int:user_id>/refeicoes', methods=['GET'])
@login_required
def read_all_user_ref(user_id):
    error = is_current_user(user_id)

    if error:
        return error

    # Filtra todas as refeições do user_id, molda um json com as informações resgatadas e repete essa operação para cada refeição encontrada no filtro de refeições
    refeicoes = Refeicao.query.filter_by(user_id=user_id).all()
    
    if refeicoes:
        return jsonify([{
            "id": refeicao.id,
            "plate_name": refeicao.plate_name,
            "description": refeicao.description,
            "weight": refeicao.weight,
            "diet": refeicao.diet,
            "date": refeicao.date.isoformat()
        }for refeicao in refeicoes])
    
    return jsonify({"mensagem": "Nenhuma refeição encontrada"}), 404


@app.route('/<int:user_id>/refeicao/<int:id_refeicao>', methods=['GET'])
@login_required
def read_refeicao(user_id, id_refeicao):
    error = is_current_user(user_id)

    if error:
        return error
    
    # Usar filter_by para fazer uma query relacionando os parâmetros e first para evitar processamento desnecessário.
    refeicao = Refeicao.query.filter_by(id=id_refeicao, user_id=user_id).first()

    if refeicao:
        return {"plate_name": refeicao.plate_name}

    return jsonify({"mensagem": "Refeição não encontrada!"}), 404


@app.route('/<int:user_id>/refeicao/<int:id_refeicao>', methods=['PATCH'])
@login_required
def update_refeicao(user_id, id_refeicao):
    error = is_current_user(user_id)

    if error:
        return error
    
    data = request.json
    refeicao = Refeicao.query.filter_by(id=id_refeicao, user_id=user_id).first()


    # Valida se o id da refeiçao existe
    if not refeicao:
        return jsonify({"mensagem": "Erro! Refeição não encontrada."}), 404 
    # Valida se pelo menos um dos campos validos existe na requisição
    if not any(key in data for key in VALID_FIELDS):
        return jsonify({"mensagem": "Nenhum dado válido enviado."}), 400

    # Percorre todos os campos válidos e substitui dinamicamente com os novos dados
    if refeicao:
        for field in VALID_FIELDS:
            if field in data:
                # Tratamento especial para o campo date
                if field == 'date':
                    try:
                        # Assume que a data está chegando no formato ISO, por exemplo: "2025-02-21T10:00:00Z"
                        date_str = data[field]
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        setattr(refeicao, field, date_obj)
                    except ValueError:
                        return jsonify({"mensagem": "Formato de data inválido. Use o formato ISO (ex: 2025-02-21T10:00:00Z)"}), 400
                else:
                    setattr(refeicao, field, data[field])

    db.session.commit()

    return jsonify ({"mensagem": f"Refeição {id_refeicao} atualizada com sucesso!"})
    
''' Bloco funcional, mas como PUT, que exige todos os parametros da var refeicao no payload
    if refeicao:
        refeicao.plate_name = data.get("plate_name")
        refeicao.weight = data.get("weight")
        refeicao.description = data.get("description")
        refeicao.diet = data.get("diet")
        date = data.get("date")
        
        db.session.commit()'''


@app.route('/<int:user_id>/refeicao/<int:id_refeicao>', methods=['DELETE'])
@login_required
def delete_refeicao(user_id, id_refeicao):
    error = is_current_user(user_id)

    if error:
        return error
    refeicao = Refeicao.query.filter_by(id=id_refeicao, user_id=user_id).first()

    if refeicao:
        db.session.delete(refeicao)
        db.session.commit()
        return jsonify({"mensagem": "Refeição deletada!"})
    
    return jsonify({"mensagem": "Refeição não encontrada."}), 404


if __name__ == '__main__':
    app.run(debug=True)