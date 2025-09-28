import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def configure_logging(app):
    """Configura el sistema de logging de la aplicación."""
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configurar el manejador de archivo rotativo
    file_handler = RotatingFileHandler(
        'logs/sis_facturacion.log',
        maxBytes=10240,  # 10MB
        backupCount=10
    )
    
    # Configurar el formato de los logs
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Configurar nivel de log
    file_handler.setLevel(app.config['LOG_LEVEL'])
    
    # Agregar manejador al logger de la aplicación
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    # Deshabilitar logging de peticiones de Werkzeug
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)
    
    app.logger.info('Iniciando Sistema de Facturación')

def create_app(config_name=None):
    """
    Factory para crear la aplicación Flask.
    
    Args:
        config_name (str): Nombre de la configuración a usar (development, testing, production)
    """
    # Determinar la configuración a usar
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Crear la aplicación
    app = Flask(__name__, 
               template_folder="templates", 
               static_folder="static")
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Configuración adicional de sesión
    app.config.update(
        SESSION_COOKIE_SECURE=config[config_name].SESSION_COOKIE_SECURE,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=config[config_name].PERMANENT_SESSION_LIFETIME
    )
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configurar login manager
    login_manager.login_view = "auth.login"
    # Desactivar mensaje automático de "Por favor inicie sesión..."
    login_manager.login_message = None
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"
    
    # Configurar logging
    configure_logging(app)
    
    # Registrar blueprints (imports relativos para evitar sombreado con app.py en raíz)
    from .routes import main_bp
    from .auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Ruta para favicon (algunos navegadores lo solicitan en la raíz)
    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='favicon.svg'))
    
    # Configurar contexto de la aplicación
    @app.shell_context_processor
    def make_shell_context():
        from .models import Usuario, Cliente, Producto, Factura, DetalleFactura
        return {
            'db': db,
            'Usuario': Usuario,
            'Cliente': Cliente,
            'Producto': Producto,
            'Factura': Factura,
            'DetalleFactura': DetalleFactura
        }
    
    # Configurar el cargador de usuarios
    @login_manager.user_loader
    def load_user(user_id):
        """Carga un usuario o cliente basado en el ID."""
        from .models import Usuario, Cliente
        
        app.logger.debug(f"Intentando cargar usuario con ID: {user_id}")
        
        # Primero intenta cargar como Usuario (administrador)
        user = db.session.get(Usuario, int(user_id)) if user_id.isdigit() else None
        
        if user:
            app.logger.debug(f"Usuario administrador cargado: {user.email}")
            return user
        
        # Si no es usuario administrador, intenta cargar como Cliente
        cliente = Cliente.query.filter_by(email=user_id).first()
        if cliente:
            app.logger.debug(f"Cliente cargado: {cliente.email}")
        else:
            app.logger.warning(f"No se encontró ningún usuario con ID: {user_id}")
            
        return cliente
    
    # Middleware para registrar información de la solicitud
    @app.before_request
    def log_request_info():
        if app.logger.isEnabledFor(logging.DEBUG) and app.config.get('LOG_REQUEST_DETAILS'):
            app.logger.debug(f"Petición: {request.method} {request.path}")
            app.logger.debug(f"Headers: {dict(request.headers)}")
            app.logger.debug(f"Sesión: {dict(session)}")
    
    # Middleware para manejar errores
    @app.errorhandler(404)
    def page_not_found(e):
        # Evitar ruido en logs por favicon faltante
        if request.path.endswith('favicon.ico'):
            return ('', 204)
        app.logger.warning(f'Página no encontrada: {request.url}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'Error interno del servidor: {e}', exc_info=True)
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning(f'Acceso denegado: {request.url}')
        return render_template('errors/403.html'), 403
    
    return app
