from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint, event
from sqlalchemy.engine import Engine


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    __table_args__ = (
        db.Index('idx_usuario_email', 'email', unique=True),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column('password', db.String(200), nullable=False)
    
    @property
    def password(self):
        # Por seguridad, nunca devolvemos la contraseña en texto
        raise AttributeError('La contraseña no se puede leer')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_admin(self) -> bool:
        return True

class Cliente(db.Model, UserMixin):
    __tablename__ = "clientes"
    __table_args__ = (
        db.Index('idx_cliente_email', 'email', unique=True),
        {'sqlite_autoincrement': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Autenticación de clientes
    password_hash = db.Column(db.String(256))
    es_cliente = db.Column(db.Boolean, default=True)

    # Métodos de autenticación
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Usamos el email como ID para Flask-Login
    def get_id(self):
        return str(self.email)

    @property
    def is_admin(self) -> bool:
        return False

class Producto(db.Model):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint('precio >= 0', name='check_precio_positivo'),
        CheckConstraint('stock >= 0', name='check_stock_no_negativo'),
        {'sqlite_autoincrement': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)  # Decimal con 2 decimales
    stock = db.Column(db.Integer, default=0, nullable=False)

class Factura(db.Model):
    __tablename__ = "facturas"
    __table_args__ = (
        db.Index('idx_factura_cliente', 'id_cliente'),
        db.Index('idx_factura_fecha', 'fecha'),
        CheckConstraint('total >= 0', name='check_total_no_negativo'),
        {'sqlite_autoincrement': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id", ondelete='RESTRICT'), nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(), nullable=False)
    total = db.Column(db.Numeric(10, 2), default=0.0, nullable=False)  # Total con 2 decimales
    
    # Relaciones
    cliente = db.relationship('Cliente', backref=db.backref('facturas', lazy=True, cascade='all, delete-orphan'))
    detalles = db.relationship('DetalleFactura', backref='factura', cascade='all, delete-orphan', lazy=True)

    def calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles)
        return self.total

    def actualizar_stock(self):
        """Resta del stock las cantidades vendidas (sin hacer commit)."""
        for detalle in self.detalles:
            # Aseguramos tener el producto (si la relación no está cargada)
            producto = detalle.producto
            if producto is None:
                producto = Producto.query.get(detalle.id_producto)
            if producto is None:
                # Si no existe el producto, seguimos con el siguiente
                continue
            # Restamos stock en memoria
            producto.stock = (producto.stock or 0) - (detalle.cantidad or 0)

class DetalleFactura(db.Model):
    __tablename__ = "detalle_factura"
    __table_args__ = (
        CheckConstraint('cantidad > 0', name='check_cantidad_positiva'),
        CheckConstraint('precio_unitario >= 0', name='check_precio_unitario_positivo'),
        CheckConstraint('subtotal >= 0', name='check_subtotal_positivo'),
        {'sqlite_autoincrement': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey("facturas.id", ondelete='CASCADE'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("productos.id", ondelete='CASCADE'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)  # 2 decimales
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)  # 2 decimales
    
    # Relaciones
    # Usamos passive_deletes=True para que, si la BD aplica ON DELETE CASCADE,
    # SQLAlchemy no necesite cargar/eliminar manualmente los hijos.
    producto = db.relationship('Producto', backref=db.backref('detalles_factura', passive_deletes=True, lazy=True))
    
    def __init__(self, **kwargs):
        super(DetalleFactura, self).__init__(**kwargs)
        self.calcular_subtotal()
    
    def calcular_subtotal(self):
        # Calcula el subtotal de la línea de factura
        # (precio unitario x cantidad)
        if self.precio_unitario is not None and self.cantidad is not None:
            self.subtotal = float(self.precio_unitario) * int(self.cantidad)
# Activar claves foráneas y cascadas en SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        # Solo aplica a conexiones SQLite
        from sqlite3 import Connection as SQLite3Connection
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    except Exception:
        # En motores que no son SQLite, este PRAGMA no aplica
        pass