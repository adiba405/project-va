from flask import Blueprint
from controllers.admin_auth_controller import admin_login, admin_profile, admin_required
from controllers.admin_controller import get_admin_stats, list_users, get_user_details, delete_user, block_user

admin_auth_bp = Blueprint('admin_auth_routes', __name__)

admin_auth_bp.route('/admin-login', methods=['GET', 'POST'])(admin_login)
admin_auth_bp.route('/admin-profile', methods=['GET'])(admin_profile)
admin_auth_bp.route('/admin-stats', methods=['GET'])(get_admin_stats)
admin_auth_bp.route('/admin-users', methods=['GET'])(list_users)
admin_auth_bp.route('/admin-users/<user_id>', methods=['GET'])(get_user_details)
admin_auth_bp.route('/admin-users/<user_id>', methods=['DELETE'])(delete_user)
admin_auth_bp.route('/admin-users/<user_id>/block', methods=['POST'])(block_user)
