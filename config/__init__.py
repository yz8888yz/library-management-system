"""Configuration"""
import os
from config.default import Config
from config.dev import DevelopmentConfig
from config.prod import ProductionConfig

config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': Config
}
