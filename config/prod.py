"""Production Configuration"""
from config.default import Config


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/library_management'
    SQLALCHEMY_ECHO = False
