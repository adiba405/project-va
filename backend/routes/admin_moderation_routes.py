from flask import Blueprint

from controllers.admin_moderation_controller import (
    list_pending_notes,
    approve_note,
    reject_note,
    list_pending_tasks,
    approve_task,
    reject_task,
    list_pending_files,
    approve_file,
    reject_file,
)

admin_moderation_bp = Blueprint('admin_moderation', __name__)

# Notes
admin_moderation_bp.route('/moderation/notes', methods=['GET'])(list_pending_notes)
admin_moderation_bp.route('/moderation/notes/<note_id>/approve', methods=['POST'])(approve_note)
admin_moderation_bp.route('/moderation/notes/<note_id>/reject', methods=['POST'])(reject_note)

# Tasks
admin_moderation_bp.route('/moderation/tasks', methods=['GET'])(list_pending_tasks)
admin_moderation_bp.route('/moderation/tasks/<task_id>/approve', methods=['POST'])(approve_task)
admin_moderation_bp.route('/moderation/tasks/<task_id>/reject', methods=['POST'])(reject_task)

# Files
admin_moderation_bp.route('/moderation/files', methods=['GET'])(list_pending_files)
admin_moderation_bp.route('/moderation/files/<file_id>/approve', methods=['POST'])(approve_file)
admin_moderation_bp.route('/moderation/files/<file_id>/reject', methods=['POST'])(reject_file)

