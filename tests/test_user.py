"""用户模块单元测试"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User
from app.services.user_service import UserService


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('test')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """提供应用上下文"""
    with app.app_context():
        yield app


def test_user_registration(app_context):
    """测试用户注册"""
    result = UserService.register_user(
        username='testuser',
        email='test@example.com',
        password='password123',
        real_name='Test User'
    )
    
    assert result['success'] is True
    assert 'data' in result
    assert result['data']['username'] == 'testuser'


def test_duplicate_username(app_context):
    """测试重复用户名"""
    UserService.register_user(
        username='testuser',
        email='test1@example.com',
        password='password123'
    )
    
    result = UserService.register_user(
        username='testuser',
        email='test2@example.com',
        password='password123'
    )
    
    assert result['success'] is False
    assert '用户名已存在' in result['message']


def test_user_authentication(app_context):
    """测试用户认证"""
    UserService.register_user(
        username='testuser',
        email='test@example.com',
        password='password123'
    )
    
    result = UserService.authenticate_user('testuser', 'password123')
    assert result['success'] is True
    assert result['data'].username == 'testuser'


def test_wrong_password(app_context):
    """测试错误密码"""
    UserService.register_user(
        username='testuser',
        email='test@example.com',
        password='password123'
    )
    
    result = UserService.authenticate_user('testuser', 'wrongpassword')
    assert result['success'] is False
    assert '密码错误' in result['message']


def test_user_password_hashing(app_context):
    """测试密码哈希"""
    user = User(
        username='testuser',
        email='test@example.com'
    )
    password = 'password123'
    user.set_password(password)
    
    assert user.check_password(password) is True
    assert user.check_password('wrongpassword') is False


def test_user_update(app_context):
    """测试用户信息更新"""
    UserService.register_user(
        username='testuser',
        email='test@example.com',
        password='password123'
    )
    
    result = UserService.update_user(1, {'real_name': 'New Name', 'phone': '13800000000'})
    
    assert result['success'] is True
    assert result['data']['real_name'] == 'New Name'
    assert result['data']['phone'] == '13800000000'


def test_change_password(app_context):
    """测试修改密码"""
    UserService.register_user(
        username='testuser',
        email='test@example.com',
        password='oldpassword'
    )
    
    result = UserService.change_password(1, 'oldpassword', 'newpassword')
    assert result['success'] is True
    
    # 验证新密码有效
    auth_result = UserService.authenticate_user('testuser', 'newpassword')
    assert auth_result['success'] is True
