from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.helpers import resp
from models.user import UserModel
from flask import current_app
from datetime import datetime
from bson import ObjectId

ADMIN_USERNAME = 'ADMIN'
ADMIN_PASSWORD = '123456789'

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        if user_id == ADMIN_USERNAME:
            return f(*args, **kwargs)

        user_model = UserModel(current_app)
        user = user_model.find_by_id(user_id)
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_login():
    if request.method == 'GET':
        return {'success': False, 'message': 'Use POST to submit credentials'}, 200

    body = request.get_json() or {}
    email = body.get('email', '').strip()
    password = body.get('password', '')

    if not email or not password:
        return resp(False, 'Email and password required', status=400)

    if email.upper() == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        auth_data = {
            'id': ADMIN_USERNAME,
            'name': 'ADMIN',
            'email': ADMIN_USERNAME,
            'role': 'admin'
        }
    else:
        user_model = UserModel(current_app)
        auth_data = user_model.authenticate(email, password)
        if not auth_data or auth_data['role'] != 'admin':
            return resp(False, 'Invalid admin credentials', status=401)

    token = create_access_token(
        identity=str(auth_data['id']),
        additional_claims={'role': 'admin'}
    )
    
    return resp(True, 'Admin login successful', {
        'token': token,
        'user': {
            'id': auth_data['id'],
            'name': auth_data['name'],
            'email': auth_data['email'],
            'role': auth_data['role']
        }
    })

@jwt_required()
def admin_profile():
    user_id = get_jwt_identity()
    if user_id == ADMIN_USERNAME:
        return resp(True, 'Admin profile', {
            'id': ADMIN_USERNAME,
            'name': 'ADMIN',
            'email': ADMIN_USERNAME,
            'role': 'admin'
        })

    user_model = UserModel(current_app)
    user = user_model.find_by_id(user_id)
    if not user or user.get('role') != 'admin':
        return resp(False, 'Admin access required', status=403)
    
    user['id'] = str(user['_id'])
    del user['_id']
    return resp(True, 'Admin profile', user)
