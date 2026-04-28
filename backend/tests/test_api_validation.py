"""
Tests de integración API para validación de nombres duplicados.
Prueba los endpoints reales HTTP con códigos de estado y respuestas esperadas.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLSession, select
from sqlmodel.pool import StaticPool

# Importar después de configurar BD
from main import app
from database import get_session
from models.categoria import Categoria
from models.ingrediente import Ingrediente
from models.producto import Producto


@pytest.fixture
def session():
    """Sesión de test con BD en memoria"""
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


@pytest.fixture
def client(session):
    """Cliente test que usa la sesión de test"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestCategoriaAPIValidation:
    """Tests de API para validación de nombres en Categorías"""

    def test_crear_categoria_exitoso(self, client: TestClient):
        """Test: POST exitoso retorna 201"""
        response = client.post(
            "/categorias", json={"nombre": "Bebidas", "descripcion": "Bebidas varias"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Bebidas"
        assert data["activo"] is True

    def test_crear_categoria_duplicada_activa_retorna_409(self, client: TestClient):
        """Test: POST con duplicate activo retorna 409 con error_code correcto"""
        # Crea primera categoría
        client.post("/categorias", json={"nombre": "Bebidas", "descripcion": "test1"})

        # Intenta crear segunda con mismo nombre
        response = client.post(
            "/categorias", json={"nombre": "Bebidas", "descripcion": "test2"}
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_NAME_ACTIVE"
        assert data["nombre"] == "Bebidas"
        assert "ya está en uso" in data["detail"]

    def test_crear_categoria_duplicada_inactiva_retorna_409(self, client: TestClient):
        """Test: POST con duplicate inactivo retorna 409 con mensaje admin"""
        # Crea y desactiva categoría
        cat_response = client.post(
            "/categorias", json={"nombre": "Bebidas", "descripcion": "test"}
        )
        cat_id = cat_response.json()["id"]

        client.delete(f"/categorias/{cat_id}")

        # Intenta crear con mismo nombre
        response = client.post(
            "/categorias", json={"nombre": "Bebidas", "descripcion": "nueva"}
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_NAME_INACTIVE"
        assert data["nombre"] == "Bebidas"
        assert "inactivo" in data["detail"]
        assert "administrador" in data["detail"]

    def test_actualizar_categoria_a_nombre_disponible_exitoso(self, client: TestClient):
        """Test: PUT a nombre único retorna 200"""
        # Crea categoría
        cat_response = client.post(
            "/categorias", json={"nombre": "Bebidas", "descripcion": "test"}
        )
        cat_id = cat_response.json()["id"]

        # Actualiza nombre
        response = client.put(
            f"/categorias/{cat_id}",
            json={"nombre": "Bebidas Premium", "descripcion": "updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Bebidas Premium"

    def test_actualizar_categoria_a_nombre_duplicado_retorna_409(
        self, client: TestClient
    ):
        """Test: PUT a nombre duplicate retorna 409"""
        # Crea dos categorías
        cat1 = client.post(
            "/categorias", json={"nombre": "Bebidas", "descripcion": "test1"}
        ).json()

        cat2 = client.post(
            "/categorias", json={"nombre": "Alimentos", "descripcion": "test2"}
        ).json()

        # Intenta cambiar cat2 al nombre de cat1
        response = client.put(
            f"/categorias/{cat2['id']}",
            json={"nombre": "Bebidas", "descripcion": "changed"},
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_NAME_ACTIVE"
        assert data["nombre"] == "Bebidas"

    def test_actualizar_categoria_al_mismo_nombre_exitoso(self, client: TestClient):
        """Test: PUT al MISMO nombre retorna 200 (sin error)"""
        # Crea categoría
        cat_response = client.post(
            "/categorias", json={"nombre": "Bebidas", "descripcion": "original"}
        )
        cat_id = cat_response.json()["id"]

        # Actualiza solo descripción (mismo nombre)
        response = client.put(
            f"/categorias/{cat_id}",
            json={"nombre": "Bebidas", "descripcion": "updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Bebidas"
        assert data["descripcion"] == "updated"


class TestIngredienteAPIValidation:
    """Tests de API para validación de nombres en Ingredientes"""

    def test_crear_ingrediente_exitoso(self, client: TestClient):
        """Test: POST exitoso retorna 201"""
        response = client.post(
            "/ingredientes", json={"nombre": "Harina", "unidad": "kg"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Harina"

    def test_crear_ingrediente_duplicado_activo_retorna_409(self, client: TestClient):
        """Test: POST con duplicate activo retorna 409"""
        client.post("/ingredientes", json={"nombre": "Harina", "unidad": "kg"})

        response = client.post(
            "/ingredientes", json={"nombre": "Harina", "unidad": "g"}
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_NAME_ACTIVE"

    def test_crear_ingrediente_duplicado_inactivo_retorna_409(self, client: TestClient):
        """Test: POST con duplicate inactivo retorna 409"""
        ing_response = client.post(
            "/ingredientes", json={"nombre": "Harina", "unidad": "kg"}
        )
        ing_id = ing_response.json()["id"]

        client.delete(f"/ingredientes/{ing_id}")

        response = client.post(
            "/ingredientes", json={"nombre": "Harina", "unidad": "kg"}
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_NAME_INACTIVE"


class TestProductoAPIValidation:
    """Tests de API para validación de nombres en Productos"""

    def test_crear_producto_exitoso(self, client: TestClient):
        """Test: POST exitoso retorna 201"""
        response = client.post(
            "/productos", json={"nombre": "Pizza Napolitana", "precio": 250.0}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Pizza Napolitana"

    def test_crear_producto_duplicado_activo_retorna_409(self, client: TestClient):
        """Test: POST con duplicate activo retorna 409"""
        client.post("/productos", json={"nombre": "Pizza Napolitana", "precio": 250.0})

        response = client.post(
            "/productos", json={"nombre": "Pizza Napolitana", "precio": 300.0}
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_NAME_ACTIVE"

    def test_crear_producto_duplicado_inactivo_retorna_409(self, client: TestClient):
        """Test: POST con duplicate inactivo retorna 409"""
        prod_response = client.post(
            "/productos", json={"nombre": "Pizza Napolitana", "precio": 250.0}
        )
        prod_id = prod_response.json()["id"]

        client.delete(f"/productos/{prod_id}")

        response = client.post(
            "/productos", json={"nombre": "Pizza Napolitana", "precio": 300.0}
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_NAME_INACTIVE"
        assert "administrador" in data["detail"]


class TestResponseFormatValidation:
    """Tests que validan el formato exacto de respuestas de error"""

    def test_response_tiene_campos_requeridos(self, client: TestClient):
        """Test: Respuesta 409 tiene detail, error_code, nombre"""
        client.post("/categorias", json={"nombre": "Test", "descripcion": "test"})

        response = client.post(
            "/categorias", json={"nombre": "Test", "descripcion": "test"}
        )

        assert response.status_code == 409
        data = response.json()

        # Campos requeridos
        assert "detail" in data
        assert "error_code" in data
        assert "nombre" in data

        # Tipos correctos
        assert isinstance(data["detail"], str)
        assert isinstance(data["error_code"], str)
        assert isinstance(data["nombre"], str)

    def test_error_code_valores_validos(self, client: TestClient):
        """Test: error_code es uno de los valores esperados"""
        client.post("/categorias", json={"nombre": "Test", "descripcion": "test"})

        response = client.post(
            "/categorias", json={"nombre": "Test", "descripcion": "test"}
        )

        data = response.json()
        assert data["error_code"] in [
            "DUPLICATE_NAME_ACTIVE",
            "DUPLICATE_NAME_INACTIVE",
        ]
