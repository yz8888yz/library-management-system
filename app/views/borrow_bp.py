"""Borrow Management Routes"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.borrow_service import BorrowService
from app.utils.decorators import librarian_required

borrow_bp = Blueprint('borrows', __name__)
borrow_service = BorrowService()


@borrow_bp.route('/my-records', methods=['GET'])
@login_required
def get_my_borrow_records():
    """获取当前用户的借阅记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')  # borrowed, returned, overdue, lost
    
    result = borrow_service.get_user_borrow_records(
        current_user.id,
        page=page,
        per_page=per_page,
        status=status
    )
    
    return jsonify({
        'code': 200,
        'data': result['data'],
        'total': result['total'],
        'page': page,
        'per_page': per_page
    })


@borrow_bp.route('', methods=['POST'])
@login_required
def borrow_book():
    """借阅图书"""
    data = request.get_json()
    
    if not data.get('book_id'):
        return jsonify({'code': 400, 'message': '缺少book_id字段'}), 400
    
    result = borrow_service.borrow_book(
        user_id=current_user.id,
        book_id=data['book_id']
    )
    
    if result['success']:
        return jsonify({'code': 201, 'message': '借阅成功', 'data': result['data']}), 201
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@borrow_bp.route('/<int:record_id>/return', methods=['POST'])
@login_required
def return_book(record_id):
    """归还图书"""
    result = borrow_service.return_book(
        record_id=record_id,
        user_id=current_user.id
    )
    
    if result['success']:
        return jsonify({'code': 200, 'message': '归还成功', 'data': result['data']})
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@borrow_bp.route('/<int:record_id>/renew', methods=['POST'])
@login_required
def renew_borrow(record_id):
    """续借"""
    result = borrow_service.renew_borrow(
        record_id=record_id,
        user_id=current_user.id
    )
    
    if result['success']:
        return jsonify({'code': 200, 'message': '续借成功', 'data': result['data']})
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@borrow_bp.route('', methods=['GET'])
@librarian_required
def get_all_borrow_records():
    """获取所有借阅记录(仅图书管理员)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    
    result = borrow_service.get_all_borrow_records(
        page=page,
        per_page=per_page,
        status=status,
        user_id=user_id
    )
    
    return jsonify({
        'code': 200,
        'data': result['data'],
        'total': result['total'],
        'page': page,
        'per_page': per_page
    })


@borrow_bp.route('/overdue-list', methods=['GET'])
@librarian_required
def get_overdue_records():
    """获取逾期借阅记录(仅图书管理员)"""
    result = borrow_service.get_overdue_records()
    
    return jsonify({
        'code': 200,
        'data': result['data'],
        'total': len(result['data'])
    })
