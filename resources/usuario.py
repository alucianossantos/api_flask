from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from hmac import compare_digest
from blacklist import *

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="O campo 'login' não pode ser nulo")
atributos.add_argument('senha', type=str, required=True, help="O campo 'senha' não pode ser nulo")

class User(Resource):

    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': f"Usuario '{user_id}' não existe!"}, 404

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except Exception as e:
                return {'message': f"Aconteceu um erro: {e}"}, 500
            return {'message': f"Usuario id '{user_id}' deletado!"}
        return {'message': f"Usuario id '{user_id}' não encontrado!"}, 200

class UserRegister(Resource):

    def post(self):
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {'message': f"O login '{dados['login']}"}
        
        user = UserModel(**dados)
        user.save_user()
        return {'message': "Usuário criado com sucesso!"}, 201

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and compare_digest(user.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=str(user.user_id))
            return {'access_token': token_de_acesso}, 200
        return {'message': 'O username ou senha está incorreto'}, 401

class UserLogout(Resource):

    @jwt_required()
    def post(self):
        # Obtém o conteúdo do JWT
        jwt_data = get_jwt()
        
        # Extrai o JTI (JWT ID) do token
        jwt_id = jwt_data['jti']
        
        # Adiciona o JTI à blacklist
        BLACKLIST.add(jwt_id)
        
        return {'message': 'Logged out successfully!'}, 200