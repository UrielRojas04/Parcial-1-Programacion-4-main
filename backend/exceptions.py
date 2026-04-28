from enum import Enum


class ErrorCode(str, Enum):
    """Códigos de error del sistema"""

    DUPLICATE_NAME_ACTIVE = "DUPLICATE_NAME_ACTIVE"
    DUPLICATE_NAME_INACTIVE = "DUPLICATE_NAME_INACTIVE"


class DuplicateNameError(Exception):
    """Excepción base para errores de nombres duplicados"""

    def __init__(self, nombre: str, error_code: ErrorCode, message: str):
        self.nombre = nombre
        self.error_code = error_code
        self.message = message
        super().__init__(message)


class DuplicateNameActiveError(DuplicateNameError):
    """Error cuando existe un nombre duplicado activo"""

    def __init__(self, nombre: str):
        message = f"El nombre '{nombre}' ya está en uso."
        super().__init__(nombre, ErrorCode.DUPLICATE_NAME_ACTIVE, message)


class DuplicateNameInactiveError(DuplicateNameError):
    """Error cuando existe un nombre duplicado inactivo (soft-deleted)"""

    def __init__(self, nombre: str):
        message = (
            f"El nombre '{nombre}' ya está en uso (inactivo). "
            "Por favor, comuníquese con el administrador para resolver este conflicto."
        )
        super().__init__(nombre, ErrorCode.DUPLICATE_NAME_INACTIVE, message)
