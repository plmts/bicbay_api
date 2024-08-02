from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from models import session, User, UserType, Transfer
from decimal import Decimal, InvalidOperation

app = Flask(__name__)
api = Api(app)

class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = session.query(User).get(user_id)
            if user:
                return jsonify({
                    'id': user.id,
                    'name': user.name,
                    'cpf': user.cpf,
                    'cnpj': user.cnpj,
                    'email': user.email,
                    'amount': str(user.amount),
                    'user_type': user.user_type.value
                })
            return {'message': 'User not found'}, 404
        else:
            users = session.query(User).all()
            return jsonify([{
                'id': user.id,
                'name': user.name,
                'cpf': user.cpf,
                'cnpj': user.cnpj,
                'email': user.email,
                'amount': str(user.amount),
                'user_type': user.user_type.value
            } for user in users])

    def post(self):
        data = request.json
        try:
            user_type_enum = UserType[data['user_type']]
        except KeyError:
            return {'message': 'Invalid user type'}, 400

        if user_type_enum == UserType.COSTUMER:
            if 'cpf' not in data or not data['cpf']:
                return {'message': 'CPF is required for costumers'}, 400
            cpf = data['cpf']
            if session.query(User).filter_by(cpf=cpf).first():
                return {'message': 'CPF already exists'}, 400
            cnpj = None
        elif user_type_enum == UserType.RETAILER:
            if 'cnpj' not in data or not data['cnpj']:
                return {'message': 'CNPJ is required for retailers'}, 400
            cnpj = data['cnpj']
            if session.query(User).filter_by(cnpj=cnpj).first():
                return {'message': 'CNPJ already exists'}, 400
            cpf = None

        new_user = User(
            name=data['name'],
            cpf=cpf,
            cnpj=cnpj,
            email=data['email'],
            password=data['password'],
            amount=data.get('amount', 1000.00),
            user_type=user_type_enum
        )
        session.add(new_user)
        session.commit()
        return {'message': 'User created', 'user_id': new_user.id}, 201

    def put(self, user_id):
        user = session.query(User).get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        data = request.json
        if 'name' in data:
            user.name = data['name']
        if 'cpf' in data and user.user_type == UserType.COSTUMER:
            if session.query(User).filter_by(cpf=data['cpf']).first():
                return {'message': 'CPF already exists'}, 400
            user.cpf = data['cpf']
        if 'cnpj' in data and user.user_type == UserType.RETAILER:
            if session.query(User).filter_by(cnpj=data['cnpj']).first():
                return {'message': 'CNPJ already exists'}, 400
            user.cnpj = data['cnpj']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password = data['password']
        if 'amount' in data:
            user.amount = data['amount']

        session.commit()
        return {'message': 'User updated'}

    def delete(self, user_id):
        user = session.query(User).get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        session.delete(user)
        session.commit()
        return {'message': 'User deleted'}

class TransferResource(Resource):
    def get(self, transfer_id=None):
        if transfer_id:
            transfer = session.query(Transfer).get(transfer_id)
            if transfer:
                return jsonify({
                    'id': transfer.id,
                    'from_user_id': transfer.from_user_id,
                    'to_user_id': transfer.to_user_id,
                    'amount': str(transfer.amount)
                })
            return {'message': 'Transfer not found'}, 404
        else:
            transfers = session.query(Transfer).all()
            return jsonify([{
                'id': transfer.id,
                'from_user_id': transfer.from_user_id,
                'to_user_id': transfer.to_user_id,
                'amount': str(transfer.amount)
            } for transfer in transfers])

    def post(self):
        data = request.json
        try:
            from_user = session.query(User).get(data['from_user_id'])
            to_user = session.query(User).get(data['to_user_id'])
            amount = Decimal(data['amount'])
        except (KeyError, InvalidOperation):
            return {'message': 'Invalid input data'}, 400

        if not from_user or not to_user:
            return {'message': 'User not found'}, 404

        if from_user.user_type == UserType.RETAILER:
            return {'message': 'Retailers cannot transfer money'}, 400

        if from_user.amount < amount:
            return {'message': 'Insufficient funds'}, 400

        from_user.amount -= amount
        to_user.amount += amount

        transfer = Transfer(from_user_id=from_user.id, to_user_id=to_user.id, amount=amount)
        session.add(transfer)
        session.commit()

        return {'message': 'Transfer completed', 'transfer_id': transfer.id}, 201

api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(TransferResource, '/transfers', '/transfers/<int:transfer_id>')

if __name__ == '__main__':
    app.run(debug=True)
