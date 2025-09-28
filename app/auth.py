from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, ClienteRegistrationForm
from .models import Usuario, Cliente
from . import db
from .constants.messages import msg

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    current_app.logger.debug("Ruta /login accedida")
    current_app.logger.debug(f"Método: {request.method}")
    if current_user.is_authenticated:
        current_app.logger.debug("Usuario ya autenticado, redirigiendo a index")
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        current_app.logger.info("==== INTENTO DE INICIO DE SESIÓN ====")
        current_app.logger.debug(f"Email proporcionado: {form.email.data}")
        user = Usuario.query.filter_by(email=form.email.data).first()
        if not user:
            user = Cliente.query.filter_by(email=form.email.data).first()

        if user:
            current_app.logger.debug("Usuario encontrado en la base de datos")
            current_app.logger.debug(f"ID del usuario: {getattr(user, 'id', 'N/A')}")
            current_app.logger.debug(f"Email del usuario: {getattr(user, 'email', 'N/A')}")
            current_app.logger.debug(f"Tipo de usuario: {'Administrador' if hasattr(user, 'password_hash') and hasattr(user, 'nombre') and hasattr(user, 'verify_password') and hasattr(user, 'id') else 'Cliente'}")
            if user.verify_password(form.password.data):
                current_app.logger.info("Contraseña válida - Iniciando sesión...")
                remember_field = getattr(form, 'remember', None)
                remember_value = remember_field.data if remember_field is not None else False
                login_user(user, remember=remember_value)
                current_app.logger.info("Usuario autenticado con éxito")
                next_page = request.args.get('next')
                current_app.logger.debug(f"Redirigiendo a: {next_page if next_page else 'main.index'}")
                return redirect(next_page or url_for('main.index'))
            else:
                current_app.logger.warning("La contraseña proporcionada no coincide")
        else:
            current_app.logger.warning(f"No se encontró ningún usuario con el email: {form.email.data}")

        flash(getattr(msg, 'INVALID_CREDENTIALS', 'Credenciales inválidas'), 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = ClienteRegistrationForm()
    if form.validate_on_submit():
        current_app.logger.info("==== REGISTRO DE NUEVO CLIENTE ====")
        current_app.logger.debug(f"Datos del formulario: {form.data}")
        direccion_field = getattr(form, 'direccion', None)
        telefono_field = getattr(form, 'telefono', None)
        cliente = Cliente(
            nombre=form.nombre.data,
            email=form.email.data,
            direccion=(direccion_field.data if direccion_field is not None else None),
            telefono=(telefono_field.data if telefono_field is not None else None)
        )
        cliente.set_password(form.password.data)

        try:
            db.session.add(cliente)
            db.session.commit()
            current_app.logger.info(f"Cliente registrado exitosamente: {cliente.email}")
            flash(getattr(msg, 'CREATE_SUCCESS', 'Creado correctamente').format('Cliente') if hasattr(msg, 'CREATE_SUCCESS') else 'Cliente creado', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al registrar cliente: {str(e)}")
            flash(getattr(msg, 'UNEXPECTED_ERROR', 'Ocurrió un error inesperado'), 'danger')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f"Cierre de sesión para el usuario: {getattr(current_user, 'email', 'N/A')}")
    logout_user()
    return redirect(url_for('main.index'))
