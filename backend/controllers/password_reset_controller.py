import os
import secrets
from datetime import datetime, timedelta

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.user import UserModel
from utils.helpers import parse_object_id, resp
from utils.email_utils import send_password_reset_email


def _get_base_url():
    # Used to build password reset link.
    # Example: http://localhost:5000 or https://yourdomain.com
    return (os.getenv('APP_BASE_URL', '').strip() or os.getenv('BASE_URL', '').strip() or 'http://localhost:5000').rstrip('/')


def _generate_reset_token():
    # Use a URL-safe token
    return secrets.token_urlsafe(32)


def _get_reset_doc_fields(token: str, expiry_minutes: int):
    return {
        'token_hash': token,  # token is random already; we can store raw for simplicity
        'expires_at': datetime.utcnow() + timedelta(minutes=expiry_minutes),
        'used': False,
    }


def _get_user_by_email(app, email: str):
    user_model = UserModel(app)
    return user_model.find_by_email(email)


def request_password_reset(app):
    body = request.get_json() or {}
    email = (body.get('email') or '').strip().lower()

    if not email:
        return resp(False, 'Email is required', status=400)

    user = _get_user_by_email(app, email)

    # Security: always respond success message even if user not found
    generic_response = resp(True, 'If the account exists, you will receive a reset email shortly.', status=200)

    if not user:
        return generic_response

    expiry_minutes = int(os.getenv('PASSWORD_RESET_EXPIRY_MINUTES', '45').strip() or '45')
    token = _generate_reset_token()

    reset_doc = {
        'user_id': user['_id'],
        'email': user.get('email'),
        'token_hash': token,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(minutes=expiry_minutes),
        'used': False,
    }

    # Keep only latest token per user (best-effort)
    try:
        app.mongo.db.password_resets.delete_many({'user_id': user['_id']})
    except Exception:
        pass

    app.mongo.db.password_resets.insert_one(reset_doc)

    reset_link = f"{_get_base_url()}/reset-password.html?token={token}"

    try:
        send_password_reset_email(email, reset_link)
    except Exception as e:
        # Do not leak details; log internally
        app.logger.error(f"Password reset email failed for {email}: {e}")
        return resp(False, 'Unable to send reset email right now. Please try again later.', status=500)

    return generic_response


def reset_password(app):
    body = request.get_json() or {}
    token = (body.get('token') or '').strip()
    new_password = (body.get('new_password') or '').strip()

    if not token:
        return resp(False, 'Token is required', status=400)

    if not new_password or len(new_password) < 6:
        return resp(False, 'New password must be at least 6 characters', status=400)

    reset = app.mongo.db.password_resets.find_one({'token_hash': token, 'used': False})
    if not reset:
        return resp(False, 'Invalid or expired token', status=400)

    if reset.get('expires_at') and reset['expires_at'] < datetime.utcnow():
        return resp(False, 'Invalid or expired token', status=400)

    user_id = reset.get('user_id')
    if not user_id:
        return resp(False, 'Invalid reset request', status=400)

    user_model = UserModel(app)

    # Reuse werkzeug hashing via UserModel.create_user helpers is not available.
    # We'll hash using generate_password_hash from werkzeug.
    from werkzeug.security import generate_password_hash

    new_hash = generate_password_hash(new_password)

    # Update password
    app.mongo.db.users.update_one({'_id': user_id}, {'$set': {'password': new_hash, 'last_active': datetime.utcnow()}})
    # Invalidate token
    app.mongo.db.password_resets.update_one({'_id': reset['_id']}, {'$set': {'used': True}})

    return resp(True, 'Password updated', status=200)

