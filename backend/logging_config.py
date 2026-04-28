"""
Logging estructurado para eventos de validación de nombres duplicados.
Captura intentos de crear/actualizar elementos con nombres duplicados.
"""

import logging
import json
from datetime import datetime
from typing import Optional
from exceptions import DuplicateNameError, ErrorCode

# Configuración de logger
logger = logging.getLogger("duplicate_name_events")

# Handler para archivo de log
log_handler = logging.FileHandler("logs/duplicate_name_events.log")
log_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.WARNING)


class DuplicateNameEvent:
    """Evento estructurado de intento de nombre duplicado"""

    def __init__(
        self,
        error_code: ErrorCode,
        nombre: str,
        entity_type: str,
        entity_id: Optional[int],
        action: str,  # "create" or "update"
        user_id: Optional[str] = None,
    ):
        self.timestamp = datetime.now().isoformat()
        self.error_code = error_code.value
        self.nombre = nombre
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.action = action
        self.user_id = user_id or "anonymous"

    def to_dict(self) -> dict:
        """Convierte evento a diccionario para serialización"""
        return {
            "timestamp": self.timestamp,
            "error_code": self.error_code,
            "nombre": self.nombre,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action,
            "user_id": self.user_id,
        }

    def to_json(self) -> str:
        """Serializa evento a JSON"""
        return json.dumps(self.to_dict())


class DuplicateNameLogger:
    """Logger centralizado para eventos de nombres duplicados"""

    # Contadores de métricas
    _metrics = {
        "DUPLICATE_NAME_ACTIVE": 0,
        "DUPLICATE_NAME_INACTIVE": 0,
    }

    @classmethod
    def log_duplicate_attempt(
        cls,
        exc: DuplicateNameError,
        entity_type: str,
        action: str,
        entity_id: Optional[int] = None,
        user_id: Optional[str] = None,
    ):
        """
        Registra un intento de crear/actualizar con nombre duplicado.

        Args:
            exc: Excepción DuplicateNameError capturada
            entity_type: Tipo de entidad ("Categoria", "Ingrediente", "Producto")
            action: Acción realizada ("create" o "update")
            entity_id: ID de la entidad siendo actualizada (None para create)
            user_id: ID del usuario que realizó la acción
        """
        event = DuplicateNameEvent(
            error_code=exc.error_code,
            nombre=exc.nombre,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
        )

        # Incrementa métrica
        cls._metrics[exc.error_code.value] += 1

        # Log en archivo (JSON para parsing)
        log_message = f"[{exc.error_code.value}] {entity_type}.{action}(nombre={exc.nombre}, id={entity_id}, user={user_id})"
        logger.warning(log_message)

        # Log también en JSON estructurado
        logger.debug(event.to_json())

    @classmethod
    def get_metrics(cls) -> dict:
        """Retorna contadores de eventos por tipo de error"""
        return cls._metrics.copy()

    @classmethod
    def reset_metrics(cls):
        """Reinicia contadores (útil para tests)"""
        cls._metrics = {
            "DUPLICATE_NAME_ACTIVE": 0,
            "DUPLICATE_NAME_INACTIVE": 0,
        }


# Funciones helper para logging en servicios
def log_duplicate_name_on_create(
    exc: DuplicateNameError,
    entity_type: str,
    user_id: Optional[str] = None,
):
    """Helper para logear errores en create"""
    DuplicateNameLogger.log_duplicate_attempt(exc, entity_type, "create", None, user_id)


def log_duplicate_name_on_update(
    exc: DuplicateNameError,
    entity_type: str,
    entity_id: int,
    user_id: Optional[str] = None,
):
    """Helper para logear errores en update"""
    DuplicateNameLogger.log_duplicate_attempt(
        exc, entity_type, "update", entity_id, user_id
    )
