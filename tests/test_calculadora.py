import pytest
from unittest.mock import MagicMock, patch
from app.app import app, procesar_calculo


# ==========================================
# 1. Pruebas Unitarias de Lógica Aritmética
# ==========================================

def test_procesar_suma():
    assert procesar_calculo(10, 25, "suma") == 35.0
    assert procesar_calculo(-5, 5, "suma") == 0.0


def test_procesar_resta():
    assert procesar_calculo(50, 20, "resta") == 30.0
    assert procesar_calculo(10, 30, "resta") == -20.0


def test_procesar_multiplicacion():
    assert procesar_calculo(6, 7, "multiplicacion") == 42.0
    assert procesar_calculo(5, 0, "multiplicacion") == 0.0


def test_procesar_division():
    assert procesar_calculo(100, 4, "division") == 25.0
    assert procesar_calculo(7, 2, "division") == 3.5


def test_procesar_division_por_cero():
    with pytest.raises(ZeroDivisionError):
        procesar_calculo(10, 0, "division")


def test_procesar_operacion_invalida():
    with pytest.raises(ValueError):
        procesar_calculo(10, 5, "potencia")


# ==========================================
# 2. Pruebas de Endpoints HTTP (Flask Client)
# ==========================================

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_ruta_inicio(client):
    response = client.get("/")
    assert response.status_code == 200
    datos = response.get_json()
    assert datos["mensaje"] == "Calculadora Python funcionando"
    assert datos["servicio"] == "calculator-app"


def test_endpoint_division_por_cero(client):
    payload = {"numero1": 15, "numero2": 0, "operacion": "division"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "No se puede dividir entre cero"


def test_endpoint_operacion_invalida(client):
    payload = {"numero1": 10, "numero2": 2, "operacion": "modulo"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Operacion no valida"


def test_endpoint_datos_incompletos(client):
    payload = {"numero1": 10}  # Falta numero2 y operacion
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


@patch("app.app.get_connection")
def test_endpoint_calculo_exitoso_mock_db(mock_get_conn, client):
    # Simular conexión y retorno de ID de PostgreSQL
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = MagicMock()
    mock_conn.execute.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn
    mock_get_conn.return_value = mock_conn

    payload = {"numero1": 20, "numero2": 30, "operacion": "suma"}
    response = client.post("/calculate", json=payload)

    assert response.status_code == 201
    datos = response.get_json()
    assert datos["id"] == 1
    assert datos["resultado"] == 50.0
    assert datos["mensaje"] == "Operacion guardada correctamente"
