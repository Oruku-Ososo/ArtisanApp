import pytest
from fastapi.testclient import TestClient
from main import app
import core

client = TestClient(app)

# Core logic tests
def test_core_greet_valid():
    assert core.greet("Alice") == "Hello, Alice!"

def test_core_greet_empty():
    with pytest.raises(ValueError):
        core.greet("")

def test_core_add_numbers():
    assert core.add_numbers(3, 4) == 7
    assert core.add_numbers(-3, -4) == -7
    assert core.add_numbers(5.5, 4.5) == 10.0

# API endpoint tests
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Greeting & Computation Service!"}

def test_api_greet_success():
    response = client.post("/greet", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json() == {"greeting": "Hello, Bob!"}

def test_api_greet_empty_name():
    response = client.post("/greet", json={"name": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Name cannot be empty"}

def test_api_greet_missing_name():
    response = client.post("/greet", json={})
    assert response.status_code == 422 # Unprocessable Entity (validation error)

def test_api_add_success():
    response = client.post("/add", json={"a": 10.5, "b": 2.5})
    assert response.status_code == 200
    assert response.json() == {"result": 13.0}

def test_api_add_invalid_input():
    response = client.post("/add", json={"a": "ten", "b": 2.5})
    assert response.status_code == 422
