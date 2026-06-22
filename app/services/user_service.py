"""User Service - Business Logic for User Management"""
from app.extensions import db
from app.models import User
from datetime import datetime


class UserService:
    """用户服务类"""
    
    @staticmethod
    def register_user(username, email, password, real_name=None):
        """
        用户注册
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            real_name: 真实姓名
        Returns:
            dict: {'success': bool, 'message': str, 'data': user_dict or None}
        """
        # 检查用户名是否存在
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': '用户名已存在'}
        
        # 检查邮箱是否存在
        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': '邮箱已存在'}
        
        try:
            # 创建新用户
            user = User(
                username=username,
                email=email,
                real_name=real_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': '注册成功',
                'data': UserService._serialize_user(user)
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'注册失败: {str(e)}'}
    
    @staticmethod
    def authenticate_user(username, password):
        """
        用户身份验证
        Args:
            username: 用户名
            password: 密码
        Returns:
            dict: {'success': bool, 'message': str, 'data': user or None}
        """
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        if not user.check_password(password):
            return {'success': False, 'message': '密码错误'}
        
        if not user.is_active_user():
            return {'success': False, 'message': '账户已被禁用'}
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return {'success': True, 'message': '认证成功', 'data': user}
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        根据ID获取用户
        Args:
            user_id: 用户ID
        Returns:
            dict: {'success': bool, 'data': user_dict or None}
        """
        user = User.query.get(user_id)
        
        if not user:
            return {'success': False, 'data': None}
        
        return {'success': True, 'data': UserService._serialize_user(user)}
    
    @staticmethod
    def update_user(user_id, data):
        """
        更新用户信息
        Args:
            user_id: 用户ID
            data: 更新数据
        Returns:
            dict: {'success': bool, 'message': str, 'data': user_dict or None}
        """
        user = User.query.get(user_id)
        
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        try:
            # 允许更新的字段
            updatable_fields = ['real_name', 'phone']
            
            for field in updatable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': '更新成功',
                'data': UserService._serialize_user(user)
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        修改密码
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
        Returns:
            dict: {'success': bool, 'message': str}
        """
        user = User.query.get(user_id)
        
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        if not user.check_password(old_password):
            return {'success': False, 'message': '旧密码错误'}
        
        try:
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'message': '密码修改成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'修改失败: {str(e)}'}
    
    @staticmethod
    def get_users_paginated(page=1, per_page=10):
        """
        分页获取用户列表
        Args:
            page: 页码
            per_page: 每页数量
        Returns:
            dict: {'data': [user_dict], 'total': int}
        """
        pagination = User.query.paginate(page=page, per_page=per_page)
        
        return {
            'data': [UserService._serialize_user(user) for user in pagination.items],
            'total': pagination.total
        }
    
    @staticmethod
    def update_user_status(user_id, status):
        """
        更新用户状态
        Args:
            user_id: 用户ID
            status: 状态(active, inactive, suspended)
        Returns:
            dict: {'success': bool, 'message': str}
        """
        valid_statuses = ['active', 'inactive', 'suspended']
        
        if status not in valid_statuses:
            return {'success': False, 'message': f'无效的状态: {status}'}
        
        user = User.query.get(user_id)
        
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        try:
            user.status = status
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'message': '状态更新成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    @staticmethod
    def _serialize_user(user):
        """序列化用户对象"""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'real_name': user.real_name,
            'phone': user.phone,
            'role': user.role,
            'status': user.status,
            'borrow_count': user.borrow_count,
            'overdue_count': user.overdue_count,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
