from app.config import Settings


def test_render_postgres_url_uses_installed_psycopg_driver():
    settings = Settings(
        secret_key="test-secret",
        database_url="postgresql://booknest:password@example.internal/booknest",
    )

    assert settings.database_url == "postgresql+psycopg://booknest:password@example.internal/booknest"


def test_sqlite_url_is_unchanged():
    settings = Settings(secret_key="test-secret", database_url="sqlite:///./booknest.db")

    assert settings.database_url == "sqlite:///./booknest.db"
