import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def configure_logging(app):
    """Configura el sistema de logging de la aplicación."""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/sis_facturacion.log',
        maxBytes=10*1024*1024,  # 10 MB reales
        backupCount=10,
        encoding='utf-8'
    )
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(app.config['LOG_LEVEL'])
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)
    
    app.logger.info('Iniciando Sistema de Facturación')

def create_app(config_name=None):
    """
    Factory para crear la aplicación Flask.
    
    Args:
        config_name (str): Nombre de la configuración a usar (development, testing, production)
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
               template_folder="templates", 
               static_folder="static")
    
    app.config.from_object(config[config_name])
    
    app.config.update(
        SESSION_COOKIE_SECURE=config[config_name].SESSION_COOKIE_SECURE,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=config[config_name].PERMANENT_SESSION_LIFETIME
    )
    
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    login_manager.login_view = "auth.login"
    login_manager.login_message = None
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"
    
    configure_logging(app)
    
    from .routes import main_bp
    from .auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='favicon.svg'))
    
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
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carga un usuario o cliente basado en el ID."""
        from .models import Usuario, Cliente
        
        app.logger.debug(f"Intentando cargar usuario con ID: {user_id}")
        
        user = db.session.get(Usuario, int(user_id)) if user_id.isdigit() else None
        
        if user:
            app.logger.debug(f"Usuario administrador cargado: {user.email}")
            return user
        
        cliente = Cliente.query.filter_by(email=user_id).first()
        if cliente:
            app.logger.debug(f"Cliente cargado: {cliente.email}")
        else:
            app.logger.warning(f"No se encontró ningún usuario con ID: {user_id}")
            
        return cliente
    
    @app.before_request
    def log_request_info():
        if app.logger.isEnabledFor(logging.DEBUG) and app.config.get('LOG_REQUEST_DETAILS'):
            app.logger.debug(f"Petición: {request.method} {request.path}")
            app.logger.debug(f"Headers: {dict(request.headers)}")
            app.logger.debug(f"Sesión: {dict(session)}")
    
    @app.errorhandler(404)
    def page_not_found(e):
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
