from datetime import datetime

from flask import current_app, request
from flask_jwt_extended import get_jwt_identity

from utils.helpers import resp, parse_object_id
from .admin_auth_controller import admin_required


def _format_item(item):
    if not item:
        return item
    item['id'] = str(item.get('_id'))
    item.pop('_id', None)

    for k in ['created_at', 'updated_at']:
        if item.get(k) is not None and hasattr(item[k], 'isoformat'):
            item[k] = item[k].isoformat()

    return item


def _list_pending(collection_name):
    db = current_app.mongo.db

    page = request.args.get('page', default=1, type=int) or 1
    limit = request.args.get('limit', default=20, type=int) or 20
    page = max(page, 1)
    limit = max(min(limit, 50), 1)

    query = {'moderation_status': 'pending'}

    total = db[collection_name].count_documents(query)
    items = list(
        db[collection_name]
        .find(query)
        .sort('updated_at', -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    items = [_format_item(i) for i in items]

    return resp(
        True,
        f'Pending {collection_name} fetched',
        {
            'items': items,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': max((total + limit - 1) // limit, 1)
        }
    )


def _set_status(collection_name, item_id, status):
    obj_id = parse_object_id(item_id, f'{collection_name[:-1]}_id')
    if obj_id is None:
        return resp(False, f'Invalid {collection_name} ID', status=400)

    db = current_app.mongo.db

    updated = db[collection_name].update_one(
        {'_id': obj_id},
        {
            '$set': {
                'moderation_status': status,
                'moderated_at': datetime.utcnow()
            }
        }
    ).modified_count

    if not updated:
        # If doc exists but status was already the same, modified_count could be 0.
        # We'll treat as success only if the document exists.
        exists = db[collection_name].find_one({'_id': obj_id}) is not None
        if not exists:
            return resp(False, f'{collection_name} not found', status=404)

    return resp(True, f'{collection_name} {status}', {'id': str(item_id)})


@admin_required
def list_pending_notes():
    return _list_pending('notes')


@admin_required
def approve_note(note_id):
    return _set_status('notes', note_id, 'approved')


@admin_required
def reject_note(note_id):
    return _set_status('notes', note_id, 'rejected')


@admin_required
def list_pending_tasks():
    return _list_pending('tasks')


@admin_required
def approve_task(task_id):
    return _set_status('tasks', task_id, 'approved')


@admin_required
def reject_task(task_id):
    return _set_status('tasks', task_id, 'rejected')


@admin_required
def list_pending_files():
    return _list_pending('files')


@admin_required
def approve_file(file_id):
    return _set_status('files', file_id, 'approved')


@admin_required
def reject_file(file_id):
    return _set_status('files', file_id, 'rejected')

