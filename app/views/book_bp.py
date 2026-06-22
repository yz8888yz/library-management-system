"""Book Management Routes"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.book_service import BookService
from app.utils.decorators import admin_required, librarian_required

book_bp = Blueprint('books', __name__)
book_service = BookService()


@book_bp.route('', methods=['GET'])
def list_books():
    """获取图书列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    
    result = book_service.get_books_paginated(
        page=page,
        per_page=per_page,
        category_id=category_id,
        search=search
    )
    
    return jsonify({
        'code': 200,
        'data': result['data'],
        'total': result['total'],
        'page': page,
        'per_page': per_page
    })


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取图书详情"""
    result = book_service.get_book_by_id(book_id)
    
    if result['success']:
        return jsonify({'code': 200, 'data': result['data']})
    else:
        return jsonify({'code': 404, 'message': '图书不存在'}), 404


@book_bp.route('', methods=['POST'])
@librarian_required
def create_book():
    """创建图书(仅图书管理员)"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['isbn', 'title', 'author', 'category_id', 'total_count']
    if not all(field in data for field in required_fields):
        return jsonify({'code': 400, 'message': '缺少必要字段'}), 400
    
    result = book_service.create_book(data)
    
    if result['success']:
        return jsonify({'code': 201, 'message': '图书创建成功', 'data': result['data']}), 201
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@book_bp.route('/<int:book_id>', methods=['PUT'])
@librarian_required
def update_book(book_id):
    """更新图书信息(仅图书管理员)"""
    data = request.get_json()
    
    result = book_service.update_book(book_id, data)
    
    if result['success']:
        return jsonify({'code': 200, 'message': '图书更新成功', 'data': result['data']})
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@book_bp.route('/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    """删除图书(仅管理员)"""
    result = book_service.delete_book(book_id)
    
    if result['success']:
        return jsonify({'code': 200, 'message': '图书删除成功'})
    else:
        return jsonify({'code': 400, 'message': result['message']}), 400


@book_bp.route('/search', methods=['GET'])
def search_books():
    """搜索图书"""
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')  # all, title, author, isbn
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    result = book_service.search_books(
        query=query,
        search_type=search_type,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'code': 200,
        'data': result['data'],
        'total': result['total'],
        'page': page,
        'per_page': per_page
    })
