"""Flask application configuration management."""

import os
from typing import Optional


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///flask_prp_wrapper.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # API settings
    API_VERSION = 'v1'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    JSON_SORT_KEYS = False
    
    # PRP Generation settings
    PRP_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), '..', 'templates')
    PRP_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'generated')
    PRP_RUNNER_PATH = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'prp_runner.py')
    
    # Research and AI settings
    OPENAI_API_KEY: Optional[str] = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY: Optional[str] = os.environ.get('ANTHROPIC_API_KEY')
    WEB_SEARCH_API_KEY: Optional[str] = os.environ.get('WEB_SEARCH_API_KEY')
    
    # Quality and validation settings
    MIN_PRP_QUALITY_SCORE = float(os.environ.get('MIN_PRP_QUALITY_SCORE', '8.0'))
    MAX_QUESTIONS_PER_SESSION = int(os.environ.get('MAX_QUESTIONS_PER_SESSION', '15'))
    RESEARCH_TIMEOUT_SECONDS = int(os.environ.get('RESEARCH_TIMEOUT_SECONDS', '300'))
    
    # Caching settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE')


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Development-specific overrides
    LOG_LEVEL = 'DEBUG'
    MIN_PRP_QUALITY_SCORE = 7.0  # Lower threshold for development


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Faster settings for testing
    RESEARCH_TIMEOUT_SECONDS = 10
    MAX_QUESTIONS_PER_SESSION = 5
    MIN_PRP_QUALITY_SCORE = 6.0


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }


# Configuration mapping
config_mapping = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration class based on environment or explicit name."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_mapping.get(config_name, DevelopmentConfig)