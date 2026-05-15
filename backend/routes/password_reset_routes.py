from flask import Blueprint, current_app

from flask import Blueprint, current_app, request, jsonify

from controllers.password_reset_controller import request_password_reset, reset_password

password_reset_bp = Blueprint('password_reset', __name__)


def _debug_method_payload(path: str):
    # Safe debug info: no secrets.
    return {
        'success': False,
        'debug': {
            'path': path,
            'method': request.method,
            'content_type': request.content_type,
        }
    }


@password_reset_bp.route('/forgot-password', methods=['POST', 'GET'])
def forgot_password():
    current_app.logger.info(
        f"[password_reset] /forgot-password hit method={request.method} content_type={request.content_type}"
    )

    if request.method != 'POST':
        return jsonify(_debug_method_payload('/forgot-password')), 405

    return request_password_reset(current_app)


@password_reset_bp.route('/reset-password', methods=['POST', 'GET'])
def do_reset_password():
    current_app.logger.info(
        f"[password_reset] /reset-password hit method={request.method} content_type={request.content_type}"
    )

    if request.method != 'POST':
        return jsonify(_debug_method_payload('/reset-password')), 405

    return reset_password(current_app)



