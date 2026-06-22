"""Borrow Service - Business Logic for Borrow Management"""
from app.extensions import db
from app.models import BorrowRecord, User, Book
from datetime import datetime, timedelta


class BorrowService:
    """借阅服务类"""
    
    @staticmethod
    def borrow_book(user_id, book_id):
        """
        用户借阅图书
        Args:
            user_id: 用户ID
            book_id: 图书ID
        Returns:
            dict: {'success': bool, 'message': str, 'data': record_dict or None}
        """
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        if not user.is_active_user():
            return {'success': False, 'message': '账户已被禁用'}
        
        book = Book.query.get(book_id)
        if not book:
            return {'success': False, 'message': '图书不存在'}
        
        if not book.is_available():
            return {'success': False, 'message': '图书暂无可用副本'}
        
        # 检查用户是否有逾期未归还的图书
        overdue_record = BorrowRecord.query.filter(
            db.and_(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status == 'borrowed',
                BorrowRecord.due_date < datetime.utcnow()
            )
        ).first()
        
        if overdue_record:
            return {'success': False, 'message': '您有逾期未归还的图书，无法借阅'}
        
        try:
            # 借出图书
            book.borrow_book()
            user.borrow_count += 1
            
            # 创建借阅记录
            record = BorrowRecord(
                user_id=user_id,
                book_id=book_id,
                borrow_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=30),
                status='borrowed'
            )
            
            db.session.add(record)
            db.session.commit()
            
            return {
                'success': True,
                'message': '借阅成功',
                'data': BorrowService._serialize_borrow_record(record)
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'借阅失败: {str(e)}'}
    
    @staticmethod
    def return_book(record_id, user_id):
        """
        用户归还图书
        Args:
            record_id: 借阅记录ID
            user_id: 用户ID
        Returns:
            dict: {'success': bool, 'message': str, 'data': record_dict or None}
        """
        record = BorrowRecord.query.get(record_id)
        
        if not record:
            return {'success': False, 'message': '借阅记录不存在'}
        
        if record.user_id != user_id:
            return {'success': False, 'message': '无权限归还此记录'}
        
        if record.status != 'borrowed':
            return {'success': False, 'message': '该图书已归还'}
        
        try:
            # 归还图书
            record.book.return_book()
            record.return_date = datetime.utcnow()
            record.status = 'returned'
            
            # 如果逾期，计算罚款
            if record.return_date > record.due_date:
                days_overdue = (record.return_date - record.due_date).days
                record.fine = days_overdue * 1.0
                record.status = 'overdue'
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '归还成功',
                'data': BorrowService._serialize_borrow_record(record)
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'归还失败: {str(e)}'}
    
    @staticmethod
    def renew_borrow(record_id, user_id):
        """
        续借图书
        Args:
            record_id: 借阅记录ID
            user_id: 用户ID
        Returns:
            dict: {'success': bool, 'message': str, 'data': record_dict or None}
        """
        record = BorrowRecord.query.get(record_id)
        
        if not record:
            return {'success': False, 'message': '借阅记录不存在'}
        
        if record.user_id != user_id:
            return {'success': False, 'message': '无权限续借此记录'}
        
        if not record.can_renew():
            return {'success': False, 'message': '无法续借(已逾期或续借次数已满)'}
        
        try:
            record.renew()
            db.session.commit()
            
            return {
                'success': True,
                'message': '续借成功',
                'data': BorrowService._serialize_borrow_record(record)
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'续借失败: {str(e)}'}
    
    @staticmethod
    def get_user_borrow_records(user_id, page=1, per_page=10, status=None):
        """
        获取用户的借阅记录
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            status: 状态过滤
        Returns:
            dict: {'data': [record_dict], 'total': int}
        """
        query = BorrowRecord.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.paginate(page=page, per_page=per_page, sort=False)
        
        return {
            'data': [BorrowService._serialize_borrow_record(record) for record in pagination.items],
            'total': pagination.total
        }
    
    @staticmethod
    def get_all_borrow_records(page=1, per_page=10, status=None, user_id=None):
        """
        获取所有借阅记录(仅管理员)
        Args:
            page: 页码
            per_page: 每页数量
            status: 状态过滤
            user_id: 用户ID过滤
        Returns:
            dict: {'data': [record_dict], 'total': int}
        """
        query = BorrowRecord.query
        
        if status:
            query = query.filter_by(status=status)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        pagination = query.paginate(page=page, per_page=per_page, sort=False)
        
        return {
            'data': [BorrowService._serialize_borrow_record(record) for record in pagination.items],
            'total': pagination.total
        }
    
    @staticmethod
    def get_overdue_records():
        """
        获取所有逾期记录
        Returns:
            dict: {'data': [record_dict]}
        """
        records = BorrowRecord.query.filter(
            db.and_(
                BorrowRecord.status == 'borrowed',
                BorrowRecord.due_date < datetime.utcnow()
            )
        ).all()
        
        return {
            'data': [BorrowService._serialize_borrow_record(record) for record in records]
        }
    
    @staticmethod
    def _serialize_borrow_record(record):
        """序列化借阅记录"""
        return {
            'id': record.id,
            'user_id': record.user_id,
            'user_name': record.user.username if record.user else None,
            'book_id': record.book_id,
            'book_title': record.book.title if record.book else None,
            'borrow_date': record.borrow_date.isoformat() if record.borrow_date else None,
            'due_date': record.due_date.isoformat() if record.due_date else None,
            'return_date': record.return_date.isoformat() if record.return_date else None,
            'renew_count': record.renew_count,
            'max_renew_count': record.max_renew_count,
            'status': record.status,
            'fine': record.fine,
            'fine_paid': record.fine_paid,
            'remarks': record.remarks,
            'created_at': record.created_at.isoformat() if record.created_at else None
        }
