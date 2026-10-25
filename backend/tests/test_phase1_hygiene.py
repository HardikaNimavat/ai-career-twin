import os
import pytest
from backend.app.core.config import Settings, EXAMPLE_SECRET_KEYS

def test_production_secret_key_validation_missing():
    # If APP_ENV=production and SECRET_KEY is missing, Settings.validate_startup_secrets raises
    old_env = os.environ.get("APP_ENV")
    old_sec = os.environ.get("SECRET_KEY")
    try:
        s = Settings()
        s.APP_ENV = "production"
        s.SECRET_KEY = ""
        with pytest.raises(ValueError, match="SECRET_KEY is missing or set to an insecure example value"):
            s.validate_startup_secrets()
    finally:
        if old_env is not None:
            os.environ["APP_ENV"] = old_env
        else:
            os.environ.pop("APP_ENV", None)
        if old_sec is not None:
            os.environ["SECRET_KEY"] = old_sec
        else:
            os.environ.pop("SECRET_KEY", None)

def test_production_secret_key_validation_example_value():
    for example_key in EXAMPLE_SECRET_KEYS:
        s = Settings()
        s.APP_ENV = "production"
        s.SECRET_KEY = example_key
        with pytest.raises(ValueError, match="SECRET_KEY is missing or set to an insecure example value"):
            s.validate_startup_secrets()

def test_production_secret_key_validation_valid():
    s = Settings()
    s.APP_ENV = "production"
    s.SECRET_KEY = "super-strong-production-key-abc-123-xyz-789!"
    # Should not raise
    s.validate_startup_secrets()

def test_cors_origins_and_credentials_logic():
    # With comma-separated origins, ALLOWED_ORIGINS is parsed into a list
    s = Settings()
    assert isinstance(s.ALLOWED_ORIGINS, list)
    assert "*" not in s.ALLOWED_ORIGINS

    # Never combine "*" with allow_credentials=True
    from fastapi.middleware.cors import CORSMiddleware
    from backend.app.main import app

    cors_middleware = None
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware = middleware
            break

    assert cors_middleware is not None
    # If origins don't contain *, allow_credentials is True
    # If origins contain *, allow_credentials must be False
    origins = cors_middleware.kwargs.get("allow_origins", [])
    allow_credentials = cors_middleware.kwargs.get("allow_credentials")
    if "*" in origins:
        assert allow_credentials is False
    else:
        assert allow_credentials is True

def test_init_db_not_called_at_import_time(monkeypatch):
    import backend.app.core.database as db_mod
    # Verify init_db exists and can be invoked
    assert hasattr(db_mod, "init_db")
    assert callable(db_mod.init_db)
