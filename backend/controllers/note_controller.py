from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from utils.helpers import parse_object_id, resp


def list_notes(app):
    user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int) or 1
    limit = request.args.get('limit', default=10, type=int) or 10
    page = max(page, 1)
    limit = max(min(limit, 50), 1)

    subject = request.args.get('subject')
    topic = request.args.get('topic')
    q = {'user_id': user_id}
    if subject:
        q['subject'] = {'$regex': subject, '$options': 'i'}
    if topic:
        q['topic'] = {'$regex': topic, '$options': 'i'}

    total = app.mongo.db.notes.count_documents(q)
    notes = list(app.mongo.db.notes.find(q)
                 .sort('updated_at', -1)

                 .skip((page - 1) * limit)
                 .limit(limit))
    for note in notes:
        note['id'] = str(note['_id'])
        note.pop('_id', None)
        note['is_shared'] = False
        note['is_owner'] = True

    return resp(True, 'Notes fetched', {
        'items': notes,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': max((total + limit - 1) // limit, 1)
    })


def create_note(app):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    subject = data.get('subject', '').strip()
    topic = data.get('topic', '').strip()
    content = data.get('content', '')
    drawing = data.get('drawing', None)
    tags = data.get('tags', [])

    if not subject or not topic:
        return resp(False, 'Subject and topic required', status=400)

    note = {
        'user_id': user_id,
        'subject': subject,
        'topic': topic,
        'content': content,
        'drawing': drawing,
        'tags': tags,
        'moderation_status': 'pending',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    note_id = app.mongo.db.notes.insert_one(note).inserted_id
    return resp(True, 'Note created', {'id': str(note_id)})


def update_note(app, note_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    note_obj_id = parse_object_id(note_id, 'note_id')
    if note_obj_id is None:
        return resp(False, 'Invalid note ID', status=400)

    note = app.mongo.db.notes.find_one({'_id': note_obj_id, 'user_id': user_id})
    if not note:
        return resp(False, 'Note not found', status=404)

    update = {}
    for key in ['subject', 'topic', 'content', 'drawing']:
        if key in data:
            update[key] = data[key]
    update['updated_at'] = datetime.utcnow()

    app.mongo.db.notes.update_one({'_id': note_obj_id}, {'$set': update})
    return resp(True, 'Note updated')


def delete_note(app, note_id):
    user_id = get_jwt_identity()
    note_obj_id = parse_object_id(note_id, 'note_id')
    if note_obj_id is None:
        return resp(False, 'Invalid note ID', status=400)

    result = app.mongo.db.notes.delete_one({'_id': note_obj_id, 'user_id': user_id})
    if result.deleted_count == 0:
        return resp(False, 'Note not found', status=404)
    return resp(True, 'Note deleted')


def get_note(app, note_id):
    user_id = get_jwt_identity()
    note_obj_id = parse_object_id(note_id, 'note_id')
    if note_obj_id is None:
        return resp(False, 'Invalid note ID', status=400)

    note = app.mongo.db.notes.find_one({'_id': note_obj_id, 'user_id': user_id})
    if not note:
        # Check if note is shared with user
        shared_note = app.mongo.db.notes.find_one({
            '_id': note_obj_id,
            'shared_with': user_id
        })
        if shared_note:
            shared_note['id'] = str(shared_note['_id'])
            shared_note.pop('_id', None)
            shared_note['is_shared'] = True
            shared_note['is_owner'] = False
            return resp(True, 'Note fetched', shared_note)
        return resp(False, 'Note not found', status=404)
    note['id'] = str(note['_id'])
    note.pop('_id', None)
    note['is_shared'] = False
    note['is_owner'] = True
    return resp(True, 'Note fetched', note)
