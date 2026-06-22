"""Borrow Record Model"""
from datetime import datetime, timedelta
from app.extensions import db


class BorrowRecord(db.Model):
    """借阅记录模型"""
    __tablename__ = 'borrow_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    
    # 借阅日期
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 应归还日期(默认30天)
    due_date = db.Column(db.DateTime, nullable=False)
    
    # 实际归还日期
    return_date = db.Column(db.DateTime)
    
    # 续借次数
    renew_count = db.Column(db.Integer, default=0)
    max_renew_count = db.Column(db.Integer, default=3)  # 最多续借3次
    
    # 状态: borrowed(借出), returned(已归还), overdue(逾期), lost(遗失)
    status = db.Column(db.String(20), default='borrowed', nullable=False, index=True)
    
    # 罚款信息
    fine = db.Column(db.Float, default=0)  # 罚款金额
    fine_paid = db.Column(db.Boolean, default=False)  # 是否已缴罚款
    
    # 备注
    remarks = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def is_overdue(self):
        """检查是否逾期"""
        if self.return_date is None and self.status == 'borrowed':
            return datetime.utcnow() > self.due_date
        return False
    
    def calculate_fine(self):
        """计算罚款(每天1元)"""
        if self.is_overdue():
            days = (datetime.utcnow() - self.due_date).days
            self.fine = days * 1.0
            return self.fine
        return 0
    
    def can_renew(self):
        """检查是否可以续借"""
        return (self.renew_count < self.max_renew_count and 
                self.status == 'borrowed' and 
                not self.is_overdue())
    
    def renew(self):
        """续借(延期30天)"""
        if self.can_renew():
            self.due_date = self.due_date + timedelta(days=30)
            self.renew_count += 1
            return True
        return False
    
    def __repr__(self):
        return f'<BorrowRecord user_id={self.user_id} book_id={self.book_id}>'
