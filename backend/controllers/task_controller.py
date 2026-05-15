from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from utils.helpers import parse_object_id, resp


def list_tasks(app):

    user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int) or 1
    limit = request.args.get('limit', default=10, type=int) or 10
    page = max(page, 1)
    limit = max(min(limit, 50), 1)

    query = {'user_id': user_id}
    total = app.mongo.db.tasks.count_documents(query)
    tasks = list(app.mongo.db.tasks.find(query)
                 .sort('deadline', 1)
                 .skip((page - 1) * limit)
                 .limit(limit))

    for task in tasks:
        task['id'] = str(task['_id'])
        task.pop('_id', None)

    return resp(True, 'Tasks fetched', {
        'items': tasks,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': max((total + limit - 1) // limit, 1)
    })


def create_task(app):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    title = body.get('title', '').strip()
    deadline = body.get('deadline', None)
    priority = body.get('priority', 'medium')  # low, medium, high

    if not title or not deadline:
        return resp(False, 'Title and deadline are required', status=400)

    if priority not in ['low', 'medium', 'high']:
        priority = 'medium'

    task = {
        'user_id': user_id,
        'title': title,
        'deadline': deadline,
        'priority': priority,
        'status': 'pending',
        'moderation_status': 'pending',
        'created_at': datetime.utcnow()
    }

    task_id = app.mongo.db.tasks.insert_one(task).inserted_id
    return resp(True, 'Task created', {'id': str(task_id)})


def update_task(app, task_id):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    task_obj_id = parse_object_id(task_id, 'task_id')
    if task_obj_id is None:
        return resp(False, 'Invalid task ID', status=400)

    data = {}
    if 'title' in body:
        data['title'] = body['title']
    if 'deadline' in body:
        data['deadline'] = body['deadline']
    if 'status' in body:
        data['status'] = body['status']

    if not data:
        return resp(False, 'No fields to update', status=400)

    result = app.mongo.db.tasks.update_one({'_id': task_obj_id, 'user_id': user_id}, {'$set': data})
    if result.matched_count == 0:
        return resp(False, 'Task not found', status=404)
    return resp(True, 'Task updated')


def delete_task(app, task_id):
    user_id = get_jwt_identity()
    task_obj_id = parse_object_id(task_id, 'task_id')
    if task_obj_id is None:
        return resp(False, 'Invalid task ID', status=400)

    result = app.mongo.db.tasks.delete_one({'_id': task_obj_id, 'user_id': user_id})
    if result.deleted_count == 0:
        return resp(False, 'Task not found', status=404)
    return resp(True, 'Task deleted')
