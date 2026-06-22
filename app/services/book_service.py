"""Book Service - Business Logic for Book Management"""
from app.extensions import db
from app.models import Book, Category
from datetime import datetime
from sqlalchemy import or_, and_


class BookService:
    """图书服务类"""
    
    @staticmethod
    def get_books_paginated(page=1, per_page=10, category_id=None, search=None):
        """
        分页获取图书列表
        Args:
            page: 页码
            per_page: 每页数量
            category_id: 分类ID(可选)
            search: 搜索关键词(可选)
        Returns:
            dict: {'data': [book_dict], 'total': int}
        """
        query = Book.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if search:
            query = query.filter(
                or_(
                    Book.title.ilike(f'%{search}%'),
                    Book.author.ilike(f'%{search}%'),
                    Book.isbn.ilike(f'%{search}%')
                )
            )
        
        pagination = query.paginate(page=page, per_page=per_page)
        
        return {
            'data': [BookService._serialize_book(book) for book in pagination.items],
            'total': pagination.total
        }
    
    @staticmethod
    def get_book_by_id(book_id):
        """
        根据ID获取图书
        Args:
            book_id: 图书ID
        Returns:
            dict: {'success': bool, 'data': book_dict or None}
        """
        book = Book.query.get(book_id)
        
        if not book:
            return {'success': False, 'data': None}
        
        return {'success': True, 'data': BookService._serialize_book(book)}
    
    @staticmethod
    def create_book(data):
        """
        创建图书
        Args:
            data: 图书数据
        Returns:
            dict: {'success': bool, 'message': str, 'data': book_dict or None}
        """
        # 检查ISBN是否已存在
        if Book.query.filter_by(isbn=data['isbn']).first():
            return {'success': False, 'message': 'ISBN已存在'}
        
        # 检查分类是否存在
        category = Category.query.get(data['category_id'])
        if not category:
            return {'success': False, 'message': '分类不存在'}
        
        try:
            book = Book(
                isbn=data['isbn'],
                title=data['title'],
                author=data['author'],
                category_id=data['category_id'],
                publisher=data.get('publisher'),
                publish_date=data.get('publish_date'),
                description=data.get('description'),
                cover_url=data.get('cover_url'),
                total_count=data['total_count'],
                available_count=data['total_count'],
                status=data.get('status', 'available')
            )
            
            db.session.add(book)
            db.session.commit()
            
            return {
                'success': True,
                'message': '图书创建成功',
                'data': BookService._serialize_book(book)
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'创建失败: {str(e)}'}
    
    @staticmethod
    def update_book(book_id, data):
        """
        更新图书信息
        Args:
            book_id: 图书ID
            data: 更新数据
        Returns:
            dict: {'success': bool, 'message': str, 'data': book_dict or None}
        """
        book = Book.query.get(book_id)
        
        if not book:
            return {'success': False, 'message': '图书不存在'}
        
        try:
            # 允许更新的字段
            updatable_fields = ['title', 'author', 'publisher', 'description', 
                              'cover_url', 'status', 'total_count', 'available_count']
            
            for field in updatable_fields:
                if field in data:
                    setattr(book, field, data[field])
            
            book.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': '更新成功',
                'data': BookService._serialize_book(book)
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    @staticmethod
    def delete_book(book_id):
        """
        删除图书
        Args:
            book_id: 图书ID
        Returns:
            dict: {'success': bool, 'message': str}
        """
        book = Book.query.get(book_id)
        
        if not book:
            return {'success': False, 'message': '图书不存在'}
        
        try:
            db.session.delete(book)
            db.session.commit()
            
            return {'success': True, 'message': '删除成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}
    
    @staticmethod
    def search_books(query, search_type='all', page=1, per_page=10):
        """
        搜索图书
        Args:
            query: 搜索关键词
            search_type: 搜索类型(all, title, author, isbn)
            page: 页码
            per_page: 每页数量
        Returns:
            dict: {'data': [book_dict], 'total': int}
        """
        search_query = Book.query
        
        if search_type == 'title':
            search_query = search_query.filter(Book.title.ilike(f'%{query}%'))
        elif search_type == 'author':
            search_query = search_query.filter(Book.author.ilike(f'%{query}%'))
        elif search_type == 'isbn':
            search_query = search_query.filter(Book.isbn.ilike(f'%{query}%'))
        else:  # all
            search_query = search_query.filter(
                or_(
                    Book.title.ilike(f'%{query}%'),
                    Book.author.ilike(f'%{query}%'),
                    Book.isbn.ilike(f'%{query}%')
                )
            )
        
        pagination = search_query.paginate(page=page, per_page=per_page)
        
        return {
            'data': [BookService._serialize_book(book) for book in pagination.items],
            'total': pagination.total
        }
    
    @staticmethod
    def _serialize_book(book):
        """序列化图书对象"""
        return {
            'id': book.id,
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'publish_date': book.publish_date.isoformat() if book.publish_date else None,
            'category_id': book.category_id,
            'category_name': book.category.name if book.category else None,
            'description': book.description,
            'cover_url': book.cover_url,
            'total_count': book.total_count,
            'available_count': book.available_count,
            'borrow_count': book.borrow_count,
            'status': book.status,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        }
