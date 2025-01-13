from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required


class Hoteis(Resource):
    def get(self):
        return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]}

class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="O campo 'nome' não pode ser nulo")
    atributos.add_argument('estrelas', type=float, required=True, help="O campo 'estrelas' não pode ser nulo")
    atributos.add_argument('diaria')
    atributos.add_argument('cidade')

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