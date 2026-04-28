from typing import TypeVar, Generic, List, Optional, Tuple
from sqlmodel import Session, select
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        statement = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "activo"):
            statement = statement.where(self.model.activo == True)
        return self.session.exec(statement).first()

    def get_all(self, offset: int = 0, limit: int = 10) -> List[T]:
        statement = select(self.model)
        if hasattr(self.model, "activo"):
            statement = statement.where(self.model.activo == True)
        statement = statement.offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, obj: T) -> T:
        self.session.merge(obj)
        self.session.flush()
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if obj:
            if hasattr(obj, "activo"):
                obj.activo = False
                self.session.merge(obj)
            else:
                self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def validate_nombre_uniqueness(
        self, nombre: str, exclude_id: Optional[int] = None
    ) -> Tuple[bool, Optional[bool]]:
        """
        Valida unicidad del campo 'nombre' considerando registros activos e inactivos.

        Retorna:
            Tuple[is_duplicate, is_active_or_none]:
            - is_duplicate: True si existe duplicado
            - is_active_or_none: True si el duplicado está activo, False si inactivo, None si no hay duplicado

        Lanza excepciones personalizadas si encuentra duplicados.
        """
        from exceptions import DuplicateNameActiveError, DuplicateNameInactiveError

        # Busca el nombre en TODOS los registros (activos e inactivos)
        statement = select(self.model).where(self.model.nombre == nombre)

        # Excluye el registro siendo actualizado (si es update, no create)
        if exclude_id is not None:
            statement = statement.where(self.model.id != exclude_id)

        duplicado = self.session.exec(statement).first()

        if duplicado:
            # Detecta si el duplicado está activo o inactivo
            if hasattr(duplicado, "activo"):
                is_active = duplicado.activo
                if is_active:
                    raise DuplicateNameActiveError(nombre)
                else:
                    raise DuplicateNameInactiveError(nombre)
            else:
                # Modelo sin soft-delete (hard delete only)
                raise DuplicateNameActiveError(nombre)

        return False, None
