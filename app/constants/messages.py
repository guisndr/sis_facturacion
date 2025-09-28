class FlashMessages:
    """Clase para manejar mensajes flash de la aplicación."""
    
    # Mensajes de éxito
    LOGIN_SUCCESS = "Inicio de sesión exitoso"
    LOGOUT_SUCCESS = "Ha cerrado sesión correctamente"
    CREATE_SUCCESS = "{} creado exitosamente"
    UPDATE_SUCCESS = "{} actualizado exitosamente"
    DELETE_SUCCESS = "{} eliminado exitosamente"
    OPERATION_SUCCESS = "Operación realizada con éxito"
    
    # Mensajes de error
    NOT_FOUND = "{} no encontrado"
    PERMISSION_DENIED = "No tiene permiso para realizar esta acción"
    INVALID_CREDENTIALS = "Credenciales inválidas"
    VALIDATION_ERROR = "Por favor corrija los errores en el formulario"
    UNEXPECTED_ERROR = "Ocurrió un error inesperado. Por favor intente nuevamente."
    DATABASE_ERROR = "Error al procesar la solicitud en la base de datos"
    
    # Mensajes de validación
    FIELD_REQUIRED = "Este campo es obligatorio"
    INVALID_EMAIL = "Ingrese un email válido"
    PASSWORD_LENGTH = "La contraseña debe tener al menos 6 caracteres"
    PASSWORDS_DONT_MATCH = "Las contraseñas no coinciden"
    INVALID_DATE_RANGE = "La fecha de inicio no puede ser posterior a la fecha final"
    
    # Mensajes de autenticación
    LOGIN_REQUIRED = "Por favor inicie sesión para acceder a esta página"
    SESSION_EXPIRED = "Su sesión ha expirado. Por favor inicie sesión nuevamente."

# Alias para facilitar el acceso
msg = FlashMessages
