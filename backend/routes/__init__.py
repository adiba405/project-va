"""
Routes package - API endpoint definitions
"""
from .auth_routes import auth_bp
from .admin_auth_routes import admin_auth_bp
from .note_routes import note_bp
from .task_routes import task_bp
from .ai_routes import ai_bp
from .user_routes import user_bp
from .share_routes import share_bp
from .file_routes import file_bp

__all__ = ['auth_bp', 'admin_auth_bp', 'note_bp', 'task_bp', 'ai_bp', 'user_bp', 'share_bp', 'file_bp']
