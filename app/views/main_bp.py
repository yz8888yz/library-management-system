"""Main Blueprint - Home and Auth Routes"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from app.services.user_service import UserService

main_bp = Blueprint('main', __name__)
user_service = UserService()


@main_bp.route('/')
def index():
    """首页"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """仪表板"""
    return render_template('dashboard.html', user=current_user)


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        data = request.get_json()
        
        # 验证输入
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'code': 400, 'message': '缺少必要字段'}), 400
        
        # 注册用户
        result = user_service.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            real_name=data.get('real_name')
        )
        
        if result['success']:
            return jsonify({'code': 200, 'message': '注册成功', 'data': result['data']})
        else:
            return jsonify({'code': 400, 'message': result['message']}), 400
    
    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'code': 400, 'message': '缺少必要字段'}), 400
        
        # 验证用户
        result = user_service.authenticate_user(
            username=data['username'],
            password=data['password']
        )
        
        if result['success']:
            user = result['data']
            login_user(user, remember=data.get('remember', False))
            return jsonify({'code': 200, 'message': '登录成功'})
        else:
            return jsonify({'code': 401, 'message': result['message']}), 401
    
    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    return redirect(url_for('main.index'))
