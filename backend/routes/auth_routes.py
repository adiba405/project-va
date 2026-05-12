from flask import Blueprint, current_app
from flask_jwt_extended import jwt_required
from controllers.auth_controller import register_user, login_user, profile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    return register_user(current_app)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if __import__('flask').request.method == 'GET':
        return {'success': False, 'message': 'Use POST to submit credentials'}, 200
    return login_user(current_app)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    return profile(current_app)
