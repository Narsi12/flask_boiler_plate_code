import jwt
import datetime
import os
from flask import request, abort, jsonify
from service.Model import db, UserSchema, User
from werkzeug.security import generate_password_hash
from service.decorators import token_required
from flask import current_app as app
from flask_restplus import Api, Resource, Namespace, fields
from service.custom_exceptions import CustomException


api = Namespace('users', description='User related information')

parser = api.parser()
parser.add_argument('x-access-tokens', location='headers')
create_user_fields = api.model('createuser', {
    'email': fields.String,
    'password': fields.String
})


class CreateUser(Resource):
    user_schema = UserSchema()

    @api.doc('create user')
    @api.doc(body=create_user_fields, parser=parser)
    def post(self):
        ''' create user '''
        payload = request.json
        errors = self.user_schema.validate(payload)
        if errors:
            abort(400, str(errors))

        if User.query.filter_by(email=payload['email']).first():
            return jsonify({'message': 'User email already registered'})
        hashed_password = generate_password_hash(payload['password'], method='sha256')
        new_user = User(email=payload['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'registered successfully'})


api.add_resource(CreateUser, '/v1/user/createuser')


class UserAuthToken(Resource):
    user_schema = UserSchema()

    @api.doc('user authorization token')
    def get(self):
        ''' authorization token  for user'''
        if not request.args:
            abort(400, "invalid parameters")
        try:
            email = request.args.get('email')
            password = request.args.get('password')
            user = User.query.filter_by(email=email).first()
            if not user:
                response = jsonify({'message': 'Invalid Credential'})
                response.status_code = 400
                return response
            if user.is_correct_password(password):
                token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() +
                                                               datetime.timedelta(minutes=30)},
                                   os.environ['SECRET_KEY'])
                return jsonify({'token': token.decode('UTF-8')})
            else:
                response = jsonify({'message': 'Invalid Credential'})
                response.status_code = 400
                return response
        except Exception as e:
            app.logger.error(
                "Exception while verifying the auth_token and  exception is: {}".format(str(e)))
            return CustomException("unable to process your request. Please try again", "500").to_dict()


api.add_resource(UserAuthToken, '/v1/user/authtoken')


class UserDetails(Resource):

    method_decorators = [token_required]

    @api.doc('user detail')
    def get(self, user, *args, **kwargs):
        ''' details of user'''
        try:
            u_info = dict()
            u_info["user_id"] = user.id
            u_info["email"] = user.email
            return jsonify(u_info)
        except Exception as e:
            app.logger.error(
                "Exception while get the user details and  exception is: {}".format(str(e)))


api.add_resource(UserDetails, '/v1/user/userdetails')
