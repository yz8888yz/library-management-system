"""Custom Decorators"""
from functools import wraps
from flask import jsonify
from flask_login import current_user


def admin_required(f):
    """要求用户为管理员"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'code': 401, 'message': '请先登录'}), 401
        
        if not current_user.is_admin():
            return jsonify({'code': 403, 'message': '只有管理员可以访问'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def librarian_required(f):
    """要求用户为图书管理员或管理员"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'code': 401, 'message': '请先登录'}), 401
        
        if not (current_user.is_librarian() or current_user.is_admin()):
            return jsonify({'code': 403, 'message': '只有图书管理员可以访问'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
