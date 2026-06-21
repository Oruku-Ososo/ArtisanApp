import pytest
from fastapi.testclient import TestClient
from main import app
import core

client = TestClient(app)

# --- System Tests ---

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "Welcome" in response.json()["data"]["message"]
    # Check custom headers
    assert "x-process-time" in response.headers
    assert "x-request-id" in response.headers

def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"

def test_api_greet_success():
    response = client.post("/greet", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json()["data"]["greeting"] == "Hello, Bob!"

def test_api_greet_validation_error():
    # Empty name fails min_length validation on Pydantic
    response = client.post("/greet", json={"name": ""})
    assert response.status_code == 422

# --- Math Tests ---

def test_api_add_success():
    response = client.post("/math/add", json={"a": 10.5, "b": 2.5})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 13.0

def test_api_subtract():
    response = client.post("/math/subtract", json={"a": 10, "b": 3})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 7.0

def test_api_multiply():
    response = client.post("/math/multiply", json={"a": 4, "b": 3})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 12.0

def test_api_divide_success():
    response = client.post("/math/divide", json={"a": 10, "b": 2})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 5.0

def test_api_divide_by_zero():
    response = client.post("/math/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert "Division by zero" in response.json()["detail"]

def test_api_power():
    response = client.post("/math/power", json={"a": 2, "b": 3})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 8.0

def test_api_sqrt_success():
    response = client.post("/math/sqrt", json={"a": 16})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 4.0

def test_api_sqrt_negative():
    response = client.post("/math/sqrt", json={"a": -1})
    assert response.status_code == 400

def test_api_factorial_success():
    response = client.post("/math/factorial", json={"n": 5})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 120

def test_api_factorial_negative():
    response = client.post("/math/factorial", json={"n": -1})
    assert response.status_code == 422 # Fails pydantic validation ge=0

def test_api_statistics_mean():
    response = client.post("/math/statistics/mean", json={"numbers": [1, 2, 3, 4, 5]})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 3.0

def test_api_statistics_variance():
    response = client.post("/math/statistics/variance", json={"numbers": [1, 2, 3]})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == 0.6666666666666666

# --- Text Tests ---

def test_api_text_analyze():
    response = client.post("/text/analyze", json={"text": "racecar"})
    assert response.status_code == 200
    data = response.json()["data"]["result"]
    assert data["char_count"] == 7
    assert data["is_palindrome"] is True

def test_api_text_transform_uppercase():
    response = client.post("/text/transform", json={"text": "hello", "operation": "uppercase"})
    assert response.status_code == 200
    assert response.json()["data"]["result"] == "HELLO"

def test_api_text_transform_invalid_op():
    response = client.post("/text/transform", json={"text": "hello", "operation": "explode"})
    assert response.status_code == 422 # Pydantic regex pattern validation

# --- Util Tests ---

def test_api_util_random_string():
    response = client.get("/utils/random-string?length=20")
    assert response.status_code == 200
    assert len(response.json()["data"]["result"]) == 20
