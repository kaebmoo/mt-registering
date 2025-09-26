# meeting-registration/config.py
import os
from datetime import timedelta
import pytz

# Load .env file at the beginning of config.py
from dotenv import load_dotenv
load_dotenv()

class Config:
    """Configuration class for Flask application"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    
    # Database configuration
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'password')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'meeting_registration')
    
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Google Apps Script URL (สำหรับส่งข้อมูลไป Google Sheets)
    GOOGLE_SCRIPT_URL = os.environ.get('GOOGLE_SCRIPT_URL', 'https://script.google.com/macros/s/xxxx/exec')
    
    # Rate limiting configuration
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Flask-Caching configuration
    CACHE_TYPE = 'RedisCache'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1') # ใช้ DB คนละตัวกับ Celery

    # Application settings
    REGISTRATION_COOLDOWN = 5  # seconds between registrations from same IP
    MAX_REGISTRATIONS_PER_IP = 50  # maximum registrations from single IP per day

    # SQLAlchemy configuration with connection pool
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Test connections before using
        'pool_timeout': 30,
        'max_overflow': 20,
        'echo_pool': True,  # Debug pool (set False in production)
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 seconds timeout
        }
    }
    
    # Database retry configuration
    DATABASE_RETRY_COUNT = int(os.environ.get('DATABASE_RETRY_COUNT', '3'))
    DATABASE_RETRY_DELAY = int(os.environ.get('DATABASE_RETRY_DELAY', '1'))
    DATABASE_RETRY_BACKOFF = os.environ.get('DATABASE_RETRY_BACKOFF', 'exponential')  # linear or exponential
    DATABASE_MAX_RETRY_DELAY = int(os.environ.get('DATABASE_MAX_RETRY_DELAY', '30'))  # max seconds
    
    # Cache configuration
    CACHE_KEY_PREFIX = os.environ.get('CACHE_KEY_PREFIX', 'meeting_reg_')
    CACHE_ACTIVE_MEETING_TIMEOUT = int(os.environ.get('CACHE_ACTIVE_MEETING_TIMEOUT', '60'))
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DATABASE_QUERIES = os.environ.get('LOG_DATABASE_QUERIES', 'false').lower() == 'true'

    # Timezone configuration
    TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Bangkok')
    TZ = pytz.timezone(TIMEZONE)
    
    # Display timezone in templates
    DISPLAY_TIMEZONE = os.environ.get('DISPLAY_TIMEZONE', 'Asia/Bangkok')
    DISPLAY_TZ = pytz.timezone(DISPLAY_TIMEZONE)

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_FROM = os.environ.get('MAIL_FROM', 'noreply@example.com')

    # Allowed email domains (comma separated)
    ALLOWED_EMAIL_DOMAINS = os.environ.get('ALLOWED_EMAIL_DOMAINS', '')  # เช่น 'company.com,organization.org'
    
    # OTP settings
    OTP_VALIDITY_MINUTES = int(os.environ.get('OTP_VALIDITY_MINUTES', 10))
    OTP_MAX_ATTEMPTS = int(os.environ.get('OTP_MAX_ATTEMPTS', 3))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
