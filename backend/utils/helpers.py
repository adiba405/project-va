import bcrypt
from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import jsonify
from werkzeug.security import check_password_hash


def hash_password(password: str) -> bytes:
    """Legacy bcrypt hash helper."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password: str, hashed) -> bool:
    """Verify password for both bcrypt and werkzeug-hashed passwords.

    - Newer users may be stored with Werkzeug's generate_password_hash (string).
    - Older users may be stored with bcrypt (bytes).
    """
    if hashed is None:
        return False

    try:
        # bcrypt hashes are bytes (or sometimes stored as bytes-like)
        if isinstance(hashed, (bytes, bytearray)):
            return bcrypt.checkpw(password.encode('utf-8'), bytes(hashed))

        # werkzeug hashes are strings like: pbkdf2:sha256:... etc
        if isinstance(hashed, str):
            return check_password_hash(hashed, password)

        # Last resort: try to coerce to str for werkzeug hashes
        return check_password_hash(str(hashed), password)
    except Exception:
        return False



def parse_object_id(value: str, field_name: str = 'id'):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def resp(success: bool, message: str, data=None, status=200):
    body = {'success': success, 'message': message}
    if data is not None:
        body['data'] = data
    return jsonify(body), status
