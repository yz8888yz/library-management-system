"""User Management Routes"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.user_service import UserService
from app.utils.decorators import admin_required

user_bp = Blueprint('users', __name__)
user_service = UserService()


@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户信息"""
    return jsonify({
        'code': 200,
        'data': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'real_name': current_user.real_name,
            'phone': current_user.phone,
            'role': current_user.role,
            'status': current_user.status,
            'borrow_count': current_user.borrow_count,
            'overdue_count': current_user.overdue_count,
            'created_at': current_user.created_at.isoformat()
        }
    })


@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户信息"""
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400
    
    result = user_service.update_user(current_user.id, data)
    
    if result['success']:
        return jsonify({'code': 200, 'message': '更新成功', 'data': result['data']})
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    data = request.get_json()
    
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'code': 400, 'message': '缺少必要字段'}), 400
    
    result = user_service.change_password(
        current_user.id,
        data['old_password'],
        data['new_password']
    )
    
    if result['success']:
        return jsonify({'code': 200, 'message': '密码修改成功'})
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@user_bp.route('', methods=['GET'])
@admin_required
def list_users():
    """获取用户列表(仅管理员)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    result = user_service.get_users_paginated(page, per_page)
    
    return jsonify({
        'code': 200,
        'data': result['data'],
        'total': result['total'],
        'page': page,
        'per_page': per_page
    })


@user_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """获取用户信息(仅管理员)"""
    result = user_service.get_user_by_id(user_id)
    
    if result['success']:
        return jsonify({'code': 200, 'data': result['data']})
    else:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404


@user_bp.route('/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """更新用户状态(仅管理员)"""
    data = request.get_json()
    
    if not data.get('status'):
        return jsonify({'code': 400, 'message': '缺少status字段'}), 400
    
    result = user_service.update_user_status(user_id, data['status'])
    
    if result['success']:
        return jsonify({'code': 200, 'message': '状态更新成功'})
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400
