from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3


def normalize_params(cidade=None, estrelas_min=0, estrelas_max=5, diaria_min=0, diaria_max=100000000, limit=50, offset=0, **dados):
    if cidade:
        return {
            "cidade": cidade,
            "estrelas_min": estrelas_min,
            "estrelas_max": estrelas_max,
            "diaria_min": diaria_min,
            "diaria_max": diaria_max,
            "limit": limit,
            "offset": offset
        }
    return {
        "estrelas_min": estrelas_min,
        "estrelas_max": estrelas_max,
        "diaria_min": diaria_min,
        "diaria_max": diaria_max,
        "limit": limit,
        "offset": offset
    }


path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)

class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect('./instance/banco.db')
        cursor = connection.cursor()
        dados = path_params.parse_args()
        dados_validos = {chave: dados[chave] for chave in dados if dados[chave] is not None}
        params = normalize_params(**dados_validos)

        if not params.get('cidade'):
            sql = "SELECT * FROM hoteis WHERE (estrelas > ? AND estrelas < ?) AND (diaria > ? AND diaria < ?) LIMIT ? OFFSET ?"
            valores = tuple([params[chave] for chave in params])
            resultado = cursor.execute(sql, valores)
        else:
            sql = "SELECT * FROM hoteis WHERE cidade = ? AND (estrelas > ? AND estrelas < ?) AND (diaria > ? AND diaria < ?) LIMIT ? OFFSET ?"
            valores = tuple([params[chave] for chave in params])
            resultado = cursor.execute(sql, valores)
        
        hoteis = []
        for linha in resultado:
            hoteis.append(
                {
                    'hotel_id': linha[0],
                    'nome': linha[1],
                    'estrelas': linha[2],
                    'diaria': linha[3],
                    'cidade': linha[4]
                }
            )
        return {'hoteis': hoteis}

        return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]}

class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="O campo 'nome' não pode ser nulo")
    atributos.add_argument('estrelas', type=float, required=True, help="O campo 'estrelas' não pode ser nulo")
    atributos.add_argument('diaria', type=float, required=True, help="O campo 'diaria' não pode ser nulo")
    atributos.add_argument('cidade', type=str, required=True, help="O campo 'cidade' não pode ser nulo")

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