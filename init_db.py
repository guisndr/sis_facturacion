from app import create_app, db
from app.models import Usuario, Cliente, Producto
from werkzeug.security import generate_password_hash, check_password_hash
import os

print("=== INICIALIZACIÓN DE LA BASE DE DATOS ===")

# Crear la aplicación
app = create_app()

with app.app_context():
    print("\n[1/4] Eliminando tablas existentes...")
    db.drop_all()
    
    print("[2/4] Creando tablas...")
    db.create_all()
    
    # Usuario de prueba
    print("\n[3/4] Creando usuario de prueba...")
    user = Usuario(
        nombre='Admin',
        email='admin@example.com',
    )
    
    # Usar el setter para hashear la contraseña
    print("  - Configurando contraseña...")
    user.password = 'admin123'  # Esto debería llamar al setter que hashea la contraseña
    
    print(f"  - Hash generado: {user.password_hash}")
    db.session.add(user)
    
    # Verificar la contraseña
    print("  - Verificando contraseña...")
    is_valid = check_password_hash(user.password_hash, 'admin123')
    print(f"  - Verificación de contraseña: {'ÉXITO' if is_valid else 'FALLÓ'}")
    
    # Cliente de prueba
    print("\n[4/4] Creando datos de prueba...")
    cliente = Cliente(
        nombre='Cliente Prueba',
        direccion='Dirección Prueba',
        telefono='123456',
        email='cliente@example.com'
    )
    db.session.add(cliente)
    
    # Productos de prueba
    prod1 = Producto(descripcion='Producto 1', precio=100.0, stock=10)
    prod2 = Producto(descripcion='Producto 2', precio=200.0, stock=20)
    db.session.add_all([prod1, prod2])
    
    # Guardar los cambios
    print("\nGuardando cambios en la base de datos...")
    db.session.commit()
    
    print("\n=== BASE DE DATOS INICIALIZADA CON ÉXITO ===")
    print("\nCredenciales de acceso:")
    print("  Email: admin@example.com")
    print("  Contraseña: admin123")
    print("\nPuedes iniciar sesión en http://127.0.0.1:5000/login")