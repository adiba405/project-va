import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from .routes.ai_routes import ai_bp
    from .routes.auth_routes import auth_bp
    from .routes.file_routes import file_bp
    from .routes.note_routes import note_bp
    from .routes.share_routes import share_bp
    from .routes.task_routes import task_bp
    from .routes.user_routes import user_bp
except ImportError:
    from routes.ai_routes import ai_bp
    from routes.auth_routes import auth_bp
    from routes.file_routes import file_bp
    from routes.note_routes import note_bp
    from routes.share_routes import share_bp
    from routes.task_routes import task_bp
    from routes.user_routes import user_bp

def create_app():
    load_dotenv(PROJECT_ROOT / '.env')
    load_dotenv(BASE_DIR / '.env')

    app = Flask(
        __name__,
        static_folder=str(PROJECT_ROOT / 'frontend'),
        static_url_path='/'
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret')
    app.config['MONGO_URI'] = os.getenv(
        'MONGO_URI',
        'mongodb://localhost:27017/ai_study_assistant'
    )
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])

    CORS(app, supports_credentials=True)
    mongo = PyMongo(app)
    jwt = JWTManager(app)

    app.mongo = mongo
    app.jwt = jwt

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(note_bp, url_prefix='/api/notes')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(share_bp, url_prefix='/api/notes')
    app.register_blueprint(file_bp, url_prefix='/api/files')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app


app = create_app()


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host=host, port=port, debug=debug)
