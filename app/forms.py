from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    DecimalField,
    IntegerField,
    SelectField,
    DateField,
    FieldList,
    FormField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    NumberRange,
)
from datetime import date
from .models import Cliente

class ClienteRegistrationForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_email(self, email):
        cliente = Cliente.query.filter_by(email=email.data).first()
        if cliente:
            raise ValidationError('Este correo ya está registrado. Por favor usa otro.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Ingresar')

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    direccion = StringField('Dirección')
    telefono = StringField('Teléfono')
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Guardar')

class ClienteCreateForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    direccion = StringField('Dirección')
    telefono = StringField('Teléfono')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Guardar')

    def validate_email(self, email):
        existente = Cliente.query.filter_by(email=email.data).first()
        if existente:
            raise ValidationError('Este correo ya está registrado. Por favor usa otro.')

class ProductoForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired()])
    precio = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[NumberRange(min=0)], default=0)
    submit = SubmitField('Guardar')

class ItemFacturaForm(FlaskForm):
    class Meta:
        csrf = False
    producto_id = SelectField('Producto', coerce=int, validators=[DataRequired()], choices=[], validate_choice=False)
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    precio_unitario = DecimalField('Precio Unitario', validators=[DataRequired(), NumberRange(min=0)])
    subtotal = DecimalField('Subtotal', render_kw={'readonly': True})

class FacturaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()], choices=[])
    fecha = DateField('Fecha', default=date.today, validators=[DataRequired()])
    items = FieldList(FormField(ItemFacturaForm), min_entries=1)
    submit = SubmitField('Guardar Factura')

class ReporteForm(FlaskForm):
    fecha_desde = DateField('Desde', validators=[DataRequired()])
    fecha_hasta = DateField('Hasta', validators=[DataRequired()])
    cliente_id = SelectField('Cliente (opcional)', coerce=int)
    submit = SubmitField('Generar Reporte')