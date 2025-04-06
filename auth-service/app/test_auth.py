from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .main import app
from .database import Base, get_db
from .auth import get_password_hash, verify_password, create_access_token
from jose import jwt
import os

class TestAuthRoutes:
    @classmethod
    def setup_class(cls):
        # Cria engine de teste com SQLite
        test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        Base.metadata.create_all(bind=test_engine)

        # Override de get_db
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        # Aplica override
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    def test_password_hash_and_verify(self):
        pw = "senha123"
        hashed = get_password_hash(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)

    def test_token_generation(self):
        token = create_access_token({"sub": "teste@example.com"})
        decoded = jwt.decode(token, os.getenv("SECRET_KEY", "secret"), algorithms=["HS256"])
        assert decoded["sub"] == "teste@example.com"

    def test_register_user(self):
        response = self.client.post("/register", json={
            "email": "teste@example.com",
            "password": "senha123"
        })
        assert response.status_code == 200
        assert response.json() == {"message": "User registered"}

    def test_register_duplicate_user(self):
        response = self.client.post("/register", json={
            "email": "teste@example.com",
            "password": "senha123"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_login_success(self):
        response = self.client.post("/login", json={
            "email": "teste@example.com",
            "password": "senha123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self):
        response = self.client.post("/login", json={
            "email": "teste@example.com",
            "password": "errada"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_nonexistent_user(self):
        response = self.client.post("/login", json={
            "email": "naoexiste@user.com",
            "password": "qualquer"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid credentials"
