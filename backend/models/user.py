from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helpers import parse_object_id

class UserModel:
    COLLECTION = 'users'
    
    def __init__(self, app):
        self.db = app.mongo.db
        self.collection = self.db[self.COLLECTION]
        
        # Ensure indexes
        self.collection.create_index('email', unique=True)
        self.collection.create_index('role')
    
    def create_user(self, name, email, password, role='user'):
        """Create new user"""
        user_data = {
            'name': name.strip(),
            'email': email.strip().lower(),
            'password': generate_password_hash(password),
            'role': role,  # 'user' or 'admin'
            'is_blocked': False,
            'ai_usage_limit': 100,
            'ai_usage_count': 0,
            'created_at': datetime.utcnow(),
            'last_active': datetime.utcnow()
        }
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def find_by_email(self, email):
        """Find user by email"""
        return self.collection.find_one({'email': email.strip().lower()})
    
    def find_by_id(self, user_id):
        """Find user by ID"""
        obj_id = parse_object_id(user_id)
        if not obj_id:
            return None
        user = self.collection.find_one({'_id': obj_id})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    def authenticate(self, email, password):
        """Authenticate user and return token payload"""
        user = self.find_by_email(email)
        if user and check_password_hash(user['password'], password):
            return {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'role': user.get('role', 'user'),
                'is_blocked': user.get('is_blocked', False)
            }
        return None
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        user = self.find_by_id(user_id)
        return user and user.get('role') == 'admin'
    
    def block_user(self, user_id, block=True):
        """Block or unblock user"""
        obj_id = parse_object_id(user_id)
        if not obj_id:
            return False
        return self.collection.update_one(
            {'_id': obj_id},
            {'$set': {'is_blocked': block}}
        ).modified_count > 0
    
    def increment_ai_usage(self, user_id):
        """Increment AI usage count for user"""
        obj_id = parse_object_id(user_id)
        if not obj_id:
            return False
        return self.collection.update_one(
            {'_id': obj_id},
            {'$inc': {'ai_usage_count': 1}, '$set': {'last_active': datetime.utcnow()}}
        ).modified_count > 0
    
    def get_admin_stats(self):
        """Get stats for admin dashboard"""
        total_users = self.collection.count_documents({})
        active_users = self.collection.count_documents({'last_active': {'$gte': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}})
        admin_users = self.collection.count_documents({'role': 'admin'})
        blocked_users = self.collection.count_documents({'is_blocked': True})
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'blocked_users': blocked_users
        }
