"""Blueprint Registration"""

def register_blueprints(app):
    """Register all blueprints"""
    from app.views.user_bp import user_bp
    from app.views.book_bp import book_bp
    from app.views.borrow_bp import borrow_bp
    from app.views.main_bp import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(book_bp, url_prefix='/api/books')
    app.register_blueprint(borrow_bp, url_prefix='/api/borrows')
