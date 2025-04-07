import os
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from app.main import app
from app.routes import get_db
from app.models import User
from app.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_password_hash_and_verify():
    password = "secret123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False

def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    exp = datetime.utcfromtimestamp(decoded["exp"])
    assert exp > datetime.utcnow()

def test_register_user():
    response = client.post("/register", json={
        "email": "user1@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered"

def test_register_duplicate_user():
    client.post("/register", json={
        "email": "user2@example.com",
        "password": "password123"
    })
    response = client.post("/register", json={
        "email": "user2@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already registered"

def test_login_valid_user():
    client.post("/register", json={
        "email": "user3@example.com",
        "password": "password123"
    })
    response = client.post("/login", json={
        "email": "user3@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    token = data["access_token"]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "user3@example.com"

def test_login_invalid_user():
    response = client.post("/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid credentials"

def test_login_wrong_password():
    client.post("/register", json={
        "email": "user4@example.com",
        "password": "password123"
    })
    response = client.post("/login", json={
        "email": "user4@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid credentials"
