"""图书模块单元测试"""
import pytest
from app import create_app
from app.extensions import db
from app.models import Book, Category
from app.services.book_service import BookService


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
def category(app_context):
    """创建测试分类"""
    category = Category(name='测试分类', description='用于测试的分类')
    db.session.add(category)
    db.session.commit()
    return category


def test_create_book(app_context, category):
    """测试创建图书"""
    result = BookService.create_book({
        'isbn': '978-7-111-64057-7',
        'title': '测试图书',
        'author': '测试作者',
        'category_id': category.id,
        'total_count': 5
    })
    
    assert result['success'] is True
    assert result['data']['title'] == '测试图书'
    assert result['data']['available_count'] == 5


def test_duplicate_isbn(app_context, category):
    """测试重复ISBN"""
    BookService.create_book({
        'isbn': '978-7-111-64057-7',
        'title': '测试图书1',
        'author': '作者1',
        'category_id': category.id,
        'total_count': 5
    })
    
    result = BookService.create_book({
        'isbn': '978-7-111-64057-7',
        'title': '测试图书2',
        'author': '作者2',
        'category_id': category.id,
        'total_count': 5
    })
    
    assert result['success'] is False
    assert 'ISBN已存在' in result['message']


def test_book_search(app_context, category):
    """测试图书搜索"""
    BookService.create_book({
        'isbn': '978-7-111-64057-7',
        'title': 'Python编程',
        'author': '张三',
        'category_id': category.id,
        'total_count': 5
    })
    
    result = BookService.search_books('Python', search_type='title')
    
    assert result['total'] == 1
    assert result['data'][0]['title'] == 'Python编程'


def test_book_availability(app_context, category):
    """测试图书可用性"""
    book_data = {
        'isbn': '978-7-111-64057-7',
        'title': '测试图书',
        'author': '测试作者',
        'category_id': category.id,
        'total_count': 1
    }
    
    result = BookService.create_book(book_data)
    book_id = result['data']['id']
    
    book = Book.query.get(book_id)
    
    assert book.is_available() is True
    
    # 借出所有副本
    book.borrow_book()
    assert book.available_count == 0
    assert book.is_available() is False


def test_book_borrow_return(app_context, category):
    """测试图书借阅和归还"""
    result = BookService.create_book({
        'isbn': '978-7-111-64057-7',
        'title': '测试图书',
        'author': '测试作者',
        'category_id': category.id,
        'total_count': 2
    })
    
    book_id = result['data']['id']
    book = Book.query.get(book_id)
    
    initial_available = book.available_count
    
    # 借阅
    book.borrow_book()
    assert book.available_count == initial_available - 1
    
    # 归还
    book.return_book()
    assert book.available_count == initial_available
