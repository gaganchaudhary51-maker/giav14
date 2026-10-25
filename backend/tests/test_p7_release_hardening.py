"""P7 release-hardening regression tests."""
import pytest

from app.auth import security


def test_production_rejects_development_or_short_signing_secret(monkeypatch):
    monkeypatch.setenv("GIA_ENV", "production")
    monkeypatch.setattr(security, "SECRET", "dev-only-change-me")
    with pytest.raises(RuntimeError, match="GIA_AUTH_SECRET"):
        security.validate_secret_configuration()
    monkeypatch.setattr(security, "SECRET", "too-short")
    with pytest.raises(RuntimeError, match="GIA_AUTH_SECRET"):
        security.validate_secret_configuration()


def test_production_accepts_long_random_secret(monkeypatch):
    monkeypatch.setenv("GIA_ENV", "production")
    monkeypatch.setattr(security, "SECRET", "a-random-production-secret-with-more-than-32-chars")
    security.validate_secret_configuration()


def test_signup_uses_least_privilege_role():
    from fastapi.testclient import TestClient
    from app.main import app
    from uuid import uuid4

    response = TestClient(app).post("/api/auth/signup", json={
        "email": f"p7-{uuid4()}@example.com",
        "password": "StrongPass123!",
        "name": "Least Privilege",
    })
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "user"
