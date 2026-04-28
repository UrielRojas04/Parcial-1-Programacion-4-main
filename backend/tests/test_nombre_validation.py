"""
Tests para validación de nombres únicos considerando soft-deletes.
"""

import pytest
from sqlmodel import Session, create_engine, SQLSession, select
from sqlmodel.pool import StaticPool
from models.categoria import Categoria
from models.ingrediente import Ingrediente
from models.producto import Producto
from uow.categoria_repository import CategoriaRepository
from uow.ingrediente_repository import IngredienteRepository
from uow.producto_repository import ProductoRepository
from exceptions import DuplicateNameActiveError, DuplicateNameInactiveError


@pytest.fixture
def session():
    """Crea una sesión de test con BD en memoria"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLSession.configure(bind=engine)
    from sqlmodel import create_all

    create_all(engine)

    with Session(engine) as session:
        yield session


class TestCategoriaValidation:
    """Tests para validación de nombres únicos en Categorías"""

    def test_crear_categoria_nombre_unico(self, session: Session):
        """Test: Crear categoría con nombre único debe exitoso"""
        repo = CategoriaRepository(session)
        cat = Categoria(nombre="Bebidas", descripcion="test")

        result = repo.create(cat)
        session.commit()

        assert result.nombre == "Bebidas"
        assert result.id is not None

    def test_crear_categoria_duplicada_activa_lanza_excepcion(self, session: Session):
        """Test: Crear categoría con nombre duplicado activo lanza DuplicateNameActiveError"""
        repo = CategoriaRepository(session)

        # Crea primera categoría
        cat1 = Categoria(nombre="Bebidas", descripcion="test")
        repo.create(cat1)
        session.commit()

        # Intenta crear segunda con el mismo nombre
        cat2 = Categoria(nombre="Bebidas", descripcion="otro")

        with pytest.raises(DuplicateNameActiveError):
            repo.create(cat2)

    def test_crear_categoria_duplicada_inactiva_lanza_excepcion(self, session: Session):
        """Test: Crear categoría con nombre de categoría inactiva lanza DuplicateNameInactiveError"""
        repo = CategoriaRepository(session)

        # Crea y desactiva una categoría
        cat1 = Categoria(nombre="Bebidas", descripcion="test")
        repo.create(cat1)
        session.commit()

        repo.delete(cat1.id)
        session.commit()

        # Intenta crear nueva con el mismo nombre
        cat2 = Categoria(nombre="Bebidas", descripcion="otro")

        with pytest.raises(DuplicateNameInactiveError):
            repo.create(cat2)

    def test_actualizar_categoria_nombre_unico(self, session: Session):
        """Test: Actualizar categoría a nombre único debe exitoso"""
        repo = CategoriaRepository(session)

        cat = Categoria(nombre="Bebidas", descripcion="test")
        repo.create(cat)
        session.commit()

        cat.nombre = "Alimentos"
        result = repo.update(cat)
        session.commit()

        assert result.nombre == "Alimentos"

    def test_actualizar_categoria_a_nombre_duplicado_lanza_excepcion(
        self, session: Session
    ):
        """Test: Actualizar a nombre duplicado lanza excepción"""
        repo = CategoriaRepository(session)

        cat1 = Categoria(nombre="Bebidas", descripcion="test1")
        cat2 = Categoria(nombre="Alimentos", descripcion="test2")
        repo.create(cat1)
        repo.create(cat2)
        session.commit()

        # Intenta cambiar nombre de cat2 al de cat1
        cat2.nombre = "Bebidas"

        with pytest.raises(DuplicateNameActiveError):
            repo.update(cat2)


class TestIngredienteValidation:
    """Tests para validación de nombres únicos en Ingredientes"""

    def test_crear_ingrediente_nombre_unico(self, session: Session):
        """Test: Crear ingrediente con nombre único debe exitoso"""
        repo = IngredienteRepository(session)
        ing = Ingrediente(nombre="Harina", unidad="kg")

        result = repo.create(ing)
        session.commit()

        assert result.nombre == "Harina"
        assert result.id is not None

    def test_crear_ingrediente_duplicado_activo_lanza_excepcion(self, session: Session):
        """Test: Crear ingrediente con nombre duplicado activo lanza excepción"""
        repo = IngredienteRepository(session)

        ing1 = Ingrediente(nombre="Harina", unidad="kg")
        repo.create(ing1)
        session.commit()

        ing2 = Ingrediente(nombre="Harina", unidad="g")

        with pytest.raises(DuplicateNameActiveError):
            repo.create(ing2)

    def test_crear_ingrediente_duplicado_inactivo_lanza_excepcion(
        self, session: Session
    ):
        """Test: Crear ingrediente con nombre de ingrediente inactivo lanza excepción"""
        repo = IngredienteRepository(session)

        ing1 = Ingrediente(nombre="Harina", unidad="kg")
        repo.create(ing1)
        session.commit()

        repo.delete(ing1.id)
        session.commit()

        ing2 = Ingrediente(nombre="Harina", unidad="kg")

        with pytest.raises(DuplicateNameInactiveError):
            repo.create(ing2)


class TestProductoValidation:
    """Tests para validación de nombres únicos en Productos"""

    def test_crear_producto_nombre_unico(self, session: Session):
        """Test: Crear producto con nombre único debe exitoso"""
        repo = ProductoRepository(session)
        prod = Producto(nombre="Pizza Napolitana", precio=250.0)

        result = repo.create(prod)
        session.commit()

        assert result.nombre == "Pizza Napolitana"
        assert result.id is not None

    def test_crear_producto_duplicado_activo_lanza_excepcion(self, session: Session):
        """Test: Crear producto con nombre duplicado activo lanza excepción"""
        repo = ProductoRepository(session)

        prod1 = Producto(nombre="Pizza Napolitana", precio=250.0)
        repo.create(prod1)
        session.commit()

        prod2 = Producto(nombre="Pizza Napolitana", precio=300.0)

        with pytest.raises(DuplicateNameActiveError):
            repo.create(prod2)

    def test_crear_producto_duplicado_inactivo_lanza_excepcion(self, session: Session):
        """Test: Crear producto con nombre de producto inactivo lanza excepción"""
        repo = ProductoRepository(session)

        prod1 = Producto(nombre="Pizza Napolitana", precio=250.0)
        repo.create(prod1)
        session.commit()

        repo.delete(prod1.id)
        session.commit()

        prod2 = Producto(nombre="Pizza Napolitana", precio=300.0)

        with pytest.raises(DuplicateNameInactiveError):
            repo.create(prod2)
