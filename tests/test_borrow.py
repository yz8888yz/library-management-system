"""借阅管理单元测试"""
import pytest
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import User, Book, Category, BorrowRecord
from app.services.user_service import UserService
from app.services.book_service import BookService
from app.services.borrow_service import BorrowService


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
def app_context(app):
    """提供应用上下文"""
    with app.app_context():
        yield app


@pytest.fixture
def test_data(app_context):
    """创建测试数据"""
    # 创建用户
    user_result = UserService.register_user(
        username='testuser',
        email='test@example.com',
        password='password123'
    )
    user = User.query.get(user_result['data']['id'])
    
    # 创建分类
    category = Category(name='测试分类')
    db.session.add(category)
    db.session.commit()
    
    # 创建图书
    book_result = BookService.create_book({
        'isbn': '978-7-111-64057-7',
        'title': '测试图书',
        'author': '测试作者',
        'category_id': category.id,
        'total_count': 3
    })
    book = Book.query.get(book_result['data']['id'])
    
    return {'user': user, 'book': book, 'category': category}


def test_borrow_book(app_context, test_data):
    """测试借阅图书"""
    user = test_data['user']
    book = test_data['book']
    
    result = BorrowService.borrow_book(user.id, book.id)
    
    assert result['success'] is True
    assert result['data']['status'] == 'borrowed'
    assert result['data']['user_id'] == user.id
    assert result['data']['book_id'] == book.id


def test_return_book(app_context, test_data):
    """测试归还图书"""
    user = test_data['user']
    book = test_data['book']
    
    borrow_result = BorrowService.borrow_book(user.id, book.id)
    record_id = borrow_result['data']['id']
    
    return_result = BorrowService.return_book(record_id, user.id)
    
    assert return_result['success'] is True
    assert return_result['data']['status'] == 'returned'


def test_renew_borrow(app_context, test_data):
    """测试续借"""
    user = test_data['user']
    book = test_data['book']
    
    borrow_result = BorrowService.borrow_book(user.id, book.id)
    record_id = borrow_result['data']['id']
    original_due_date = datetime.fromisoformat(borrow_result['data']['due_date'])
    
    renew_result = BorrowService.renew_borrow(record_id, user.id)
    
    assert renew_result['success'] is True
    new_due_date = datetime.fromisoformat(renew_result['data']['due_date'])
    
    # 新期限应该晚30天
    assert (new_due_date - original_due_date).days == 30
    assert renew_result['data']['renew_count'] == 1


def test_cannot_borrow_when_overdue(app_context, test_data):
    """测试逾期时无法借阅"""
    user = test_data['user']
    book = test_data['book']
    
    # 创建一个逾期的借阅记录
    record = BorrowRecord(
        user_id=user.id,
        book_id=book.id,
        borrow_date=datetime.utcnow() - timedelta(days=60),
        due_date=datetime.utcnow() - timedelta(days=30),
        status='borrowed'
    )
    db.session.add(record)
    db.session.commit()
    
    # 创建另一本书
    from app.models import Category
    category = Category.query.first()
    book2_result = BookService.create_book({
        'isbn': '978-7-111-64058-4',
        'title': '另一本书',
        'author': '作者',
        'category_id': category.id,
        'total_count': 2
    })
    book2 = Book.query.get(book2_result['data']['id'])
    
    # 尝试借阅新书应该失败
    result = BorrowService.borrow_book(user.id, book2.id)
    
    assert result['success'] is False
    assert '逾期' in result['message']


def test_get_user_borrow_records(app_context, test_data):
    """测试获取用户借阅记录"""
    user = test_data['user']
    book = test_data['book']
    
    BorrowService.borrow_book(user.id, book.id)
    
    result = BorrowService.get_user_borrow_records(user.id)
    
    assert result['total'] >= 1
    assert len(result['data']) >= 1
    assert result['data'][0]['user_id'] == user.id
