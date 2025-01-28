from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
from resources.filtros import *
import sqlite3

path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str, location='args')
path_params.add_argument('estrelas_min', type=float, location='args')
path_params.add_argument('estrelas_max', type=float, location='args')
path_params.add_argument('diaria_min', type=float, location='args')
path_params.add_argument('diaria_max', type=float, location='args')
path_params.add_argument('limit', type=int, location='args')
path_params.add_argument('offset', type=int, location='args')
path_params.add_argument('order_by', type=str, location='args')

class Hoteis(Resource):
    def get(self):
        try:
            connection = sqlite3.connect('./instance/banco.db')
            cursor = connection.cursor()

            dados = path_params.parse_args()
            dados_validos = {chave: dados[chave] for chave in dados if dados[chave] is not None}
            params = normalize_params(**dados_validos)
        except Exception as e:
            return {'message': f'Erro na conexão com o servidor: {e}'}, 500

        try:
            if not params.get('cidade'):
                sql = consulta_sem_cidade(params)
                resultado = cursor.execute(sql)
            else:
                sql = consulta_com_cidade(params)
                resultado = cursor.execute(sql)
            
            hoteis = []
            for linha in resultado:
                hoteis.append(
                    {
                        'hotel_id': str(linha[0]).lower(),
                        'nome': str(linha[1]).capitalize(),
                        'estrelas': linha[2],
                        'diaria': linha[3],
                        'cidade': str(linha[4]).capitalize(),
                        'site_id': linha[5]
                    }
                )
            return {'hoteis': hoteis}
        except Exception as e:
            return {'message': f'Erro no banco: {e}'}, 500
        finally:
            connection.close()

        # return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]}

class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="O campo 'nome' não pode ser nulo")
    atributos.add_argument('estrelas', type=float, required=True, help="O campo 'estrelas' não pode ser nulo")
    atributos.add_argument('diaria', type=float, required=True, help="O campo 'diaria' não pode ser nulo")
    atributos.add_argument('cidade', type=str, required=True, help="O campo 'cidade' não pode ser nulo")
    atributos.add_argument('site_id', type=int, required=True, help="Todo hotel deve estar ligado a um site")

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': f'Hotel {hotel_id} não existe!'}, 404
    
    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": f"Hotel id '{hotel_id}' já existe"}, 400
        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except Exception as e:
            return {'message': f"Aconteceu um erro: {e}"}, 500
        return hotel.json()
    
    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.atributos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return {'message': f'Hotel atualizado!', 'hotel': hotel_encontrado.json()}, 200
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except Exception as e:
            return {'message': f"Aconteceu um erro: {e}"}, 500
        return {'message': f'Hotel criado com sucesso!', 'hotel': hotel.json()}, 201

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except Exception as e:
                return {'message': f"Aconteceu um erro: {e}"}, 500
            return {'message': f"Hotel id '{hotel_id}' deletado!"}
        return {'message': f"Hotel id '{hotel_id}' não encontrado!"}, 200