from typing import TypeVar, Generic, List, Optional
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