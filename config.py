import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-predeterminada-cambiar-en-produccion'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    STRING_LENGTHS = {
        'email': 120,
        'nombre': 100,
        'direccion': 200,
        'telefono': 20,
        'descripcion': 200,
        'password': 256
    }
    PRECISION_PRECIO = 10
    DECIMAL_PLACES = 2
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/sis_facturacion.log'
    LOG_REQUEST_DETAILS = False
    ITEMS_PER_PAGE = 20
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///facturacion.db'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///sis_facturacion_dev.db'
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """Configuración para pruebas."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'WARNING'


class ProductionConfig(Config):
    """Configuración para producción."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sis_facturacion_prod.db'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    LOG_LEVEL = 'WARNING'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno actual."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

if not os.path.exists('logs'):
    os.makedirs('logs')

