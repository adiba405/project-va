from flask import Blueprint
from controllers.admin_auth_controller import admin_login, admin_profile, admin_required

admin_auth_bp = Blueprint('admin_auth_routes', __name__)

admin_auth_bp.route('/admin-login', methods=['POST'])(admin_login)
admin_auth_bp.route('/admin-profile', methods=['GET'])(admin_profile)
