"""User Model"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # 用户角色: admin(管理员), librarian(图书管理员), user(普通用户)
    role = db.Column(db.String(20), default='user', nullable=False)
    
    # 账户状态: active(激活), inactive(未激活), suspended(被禁用)
    status = db.Column(db.String(20), default='active', nullable=False)
    
    # 借阅次数、逾期次数
    borrow_count = db.Column(db.Integer, default=0)
    overdue_count = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # 关系
    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == 'admin'
    
    def is_librarian(self):
        """检查是否为图书管理员"""
        return self.role == 'librarian'
    
    def is_active_user(self):
        """检查账户是否激活"""
        return self.status == 'active'
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader"""
    return User.query.get(int(user_id))
