"""Book and Category Models"""
from datetime import datetime
from app.extensions import db


class Category(db.Model):
    """图书分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    books = db.relationship('Book', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Book(db.Model):
    """图书模型"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    publisher = db.Column(db.String(100))
    publish_date = db.Column(db.Date)
    
    # 图书分类
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # 描述和封面
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    
    # 库存和借阅信息
    total_count = db.Column(db.Integer, default=0, nullable=False)  # 总数量
    available_count = db.Column(db.Integer, default=0, nullable=False)  # 可用数量
    borrow_count = db.Column(db.Integer, default=0)  # 被借阅次数
    
    # 图书状态: available(可用), unavailable(不可用), deprecated(已下架)
    status = db.Column(db.String(20), default='available', nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def is_available(self):
        """检查是否可借阅"""
        return self.status == 'available' and self.available_count > 0
    
    def borrow_book(self):
        """借阅图书"""
        if self.available_count > 0:
            self.available_count -= 1
            self.borrow_count += 1
            return True
        return False
    
    def return_book(self):
        """归还图书"""
        if self.available_count < self.total_count:
            self.available_count += 1
            return True
        return False
    
    def __repr__(self):
        return f'<Book {self.title}>'
