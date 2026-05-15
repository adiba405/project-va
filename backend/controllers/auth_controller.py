from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from utils.helpers import check_password, hash_password, parse_object_id, resp
from models.user import UserModel


def register_user(app):
    body = request.get_json() or {}
    name = body.get('name', '').strip()
    email = body.get('email', '').strip().lower()
    password = body.get('password', '')

    app.logger.info(f"Register attempt: email={email}")


    if not name or not email or not password:
        return resp(False, 'Name, email, and password are required', status=400)

    if app.mongo.db.users.find_one({'email': email}):
        return resp(False, 'User already exists', status=409)

    user_model = UserModel(app)
    user_id = user_model.create_user(name, email, password)
    return resp(True, 'User registered', {'user_id': user_id})


def login_user(app):

    body = request.get_json() or {}
    email = body.get('email', '').strip().lower()
    password = body.get('password', '')

    if not email or not password:
        return resp(False, 'Email and password are required', status=400)

    user = app.mongo.db.users.find_one({'email': email})
    if not user or not check_password(password, user['password']):
        return resp(False, 'Invalid credentials', status=401)

    token = create_access_token(identity=str(user['_id']))
    return resp(True, 'Login successful', {'token': token, 'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email']}})


@jwt_required()
def profile(app):
    user_id = get_jwt_identity()
    user_obj_id = parse_object_id(user_id, 'user_id')
    if user_obj_id is None:
        return resp(False, 'Invalid user ID', status=400)

    user = app.mongo.db.users.find_one({'_id': user_obj_id}, {'password': False})
    if not user:
        return resp(False, 'User not found', status=404)
    user['id'] = str(user['_id'])
    del user['_id']
    return resp(True, 'Profile fetched', user)
