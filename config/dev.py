"""Development Configuration"""
from config.default import Config


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/library_management'
    SQLALCHEMY_ECHO = True  # SQL语句日志
