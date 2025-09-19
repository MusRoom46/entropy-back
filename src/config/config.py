import os


def _split_csv(raw, default):
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


def _split_origins(raw):
    return _split_csv(raw, [
        "https://entropy-front.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000",
    ])


def _as_bool(value, default):
    if value is None:
        return default
    return value.lower() in {"true", "1", "yes", "on"}


DEFAULT_ENV = "production" if os.getenv("RENDER") else "development"


class Config:
    # PostgreSQL connection string
    DB_USER = os.getenv("POSTGRES_USER", "entropy_user")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "entropy_pass")
    DB_HOST = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost"))
    DB_PORT = os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "entropy_db"))

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secrets for encryption and JWT
    AES_KEY = os.getenv("AES_KEY", "this_is_a_32_characters_secret_key!!")
    JWT_SECRET = "this_is_a_32_characters_secret_key!!"

    # Cross origin and cookie handling
    CORS_ALLOWED_ORIGINS = _split_origins(os.getenv("CORS_ALLOWED_ORIGINS"))
    CORS_ALLOW_HEADERS = _split_csv(os.getenv("CORS_ALLOW_HEADERS"), ["Content-Type", "Authorization"])
    CORS_EXPOSE_HEADERS = _split_csv(os.getenv("CORS_EXPOSE_HEADERS"), ["Content-Type", "Authorization"])
    ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("FLASK_ENV", DEFAULT_ENV)).lower()
    COOKIE_SECURE = _as_bool(os.getenv("COOKIE_SECURE"), ENVIRONMENT == "production")
    COOKIE_SAMESITE = os.getenv(
        "COOKIE_SAMESITE",
        "None" if ENVIRONMENT == "production" else "Lax",
    )

    if COOKIE_SAMESITE.lower() == "none" and not COOKIE_SECURE:
        COOKIE_SECURE = True
