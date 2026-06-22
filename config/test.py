"""Test Configuration"""
from config.default import Config


class TestConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    
    # 使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
