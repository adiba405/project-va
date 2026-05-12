from datetime import datetime
from flask import current_app, request
from .admin_auth_controller import admin_required
from utils.helpers import resp, parse_object_id


def _format_user(user):
    user['id'] = str(user['_id'])
    user.pop('_id', None)
    if 'created_at' in user and user['created_at'] is not None:
        user['created_at'] = user['created_at'].isoformat()
    if 'last_active' in user and user['last_active'] is not None:
        user['last_active'] = user['last_active'].isoformat()
    return user


@admin_required
def get_admin_stats():
    db = current_app.mongo.db
    total_users = db.users.count_documents({})
    total_notes = db.notes.count_documents({})
    total_tasks = db.tasks.count_documents({})
    total_files = db.files.count_documents({})
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    active_users = db.users.count_documents({'last_active': {'$gte': start_of_day}})
    pending_tasks = db.tasks.count_documents({'status': {'$ne': 'completed'}})
    shared_notes = db.notes.count_documents({'shared_with': {'$exists': True, '$ne': []}})
    blocked_users = db.users.count_documents({'is_blocked': True})
    admin_users = db.users.count_documents({'role': 'admin'})

    return resp(True, 'Admin stats fetched', {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'blocked_users': blocked_users,
        'total_notes': total_notes,
        'total_tasks': total_tasks,
        'total_files': total_files,
        'pending_tasks': pending_tasks,
        'shared_notes': shared_notes
    })


@admin_required
def list_users():
    users = list(current_app.mongo.db.users.find({}, {'password': False}).sort('created_at', -1).limit(18))
    users = [_format_user(u) for u in users]
    return resp(True, 'Admin users fetched', users)


@admin_required
def get_user_details(user_id):
    obj_id = parse_object_id(user_id)
    if not obj_id:
        return resp(False, 'Invalid user ID', status=400)

    user = current_app.mongo.db.users.find_one({'_id': obj_id}, {'password': False})
    if not user:
        return resp(False, 'User not found', status=404)

    return resp(True, 'User details fetched', _format_user(user))


@admin_required
def delete_user(user_id):
    obj_id = parse_object_id(user_id)
    if not obj_id:
        return resp(False, 'Invalid user ID', status=400)

    user = current_app.mongo.db.users.find_one({'_id': obj_id}, {'password': False})
    if not user:
        return resp(False, 'User not found', status=404)

    if user.get('role') == 'admin':
        return resp(False, 'Cannot remove an admin account', status=403)

    deleted = current_app.mongo.db.users.delete_one({'_id': obj_id}).deleted_count
    if not deleted:
        return resp(False, 'User could not be removed', status=500)

    return resp(True, 'User removed successfully', {'id': str(user_id)})


@admin_required
def block_user(user_id):
    obj_id = parse_object_id(user_id)
    if not obj_id:
        return resp(False, 'Invalid user ID', status=400)

    body = request.get_json(silent=True) or {}
    block = bool(body.get('block', True))
    updated = current_app.mongo.db.users.update_one(
        {'_id': obj_id},
        {'$set': {'is_blocked': block}}
    ).modified_count

    if not updated:
        return resp(False, 'Unable to update user status', status=500)

    status_text = 'blocked' if block else 'unblocked'
    return resp(True, f'User {status_text} successfully', {'id': str(user_id), 'is_blocked': block})
