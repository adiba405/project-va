from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.helpers import resp
from models.user import UserModel
from flask import current_app
from datetime import datetime
from bson import ObjectId

admin_auth_bp = Blueprint('admin_auth', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user_model = UserModel(current_app)
        user = user_model.find_by_id(user_id)
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    body = request.get_json() or {}
    email = body.get('email', '').strip().lower()
    password = body.get('password', '')

    if not email or not password:
        return resp(False, 'Email and password required', status=400)

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

@admin_auth_bp.route('/admin-profile', methods=['GET'])
@jwt_required()
def admin_profile():
    user_id = get_jwt_identity()
    user_model = UserModel(current_app)
    user = user_model.find_by_id(user_id)
    if not user or user.get('role') != 'admin':
        return resp(False, 'Admin access required', status=403)
    
    user['id'] = str(user['_id'])
    del user['_id']
    return resp(True, 'Admin profile', user)
