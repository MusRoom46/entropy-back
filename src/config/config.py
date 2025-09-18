import os


class Config:
    # URI de connexion PostgreSQL
    # Prefer DATABASE_URL if provided; otherwise, build from individual parts with proper format.
    DB_USER = os.getenv("POSTGRES_USER", "entropy_user")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "entropy_pass")
    DB_HOST = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost"))
    DB_PORT = os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "entropy_db"))

    # If DATABASE_URL provided, use it; else construct a proper URL.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète pour AES (16, 24 ou 32 octets)
    AES_KEY = os.getenv("AES_KEY", "this_is_a_32_characters_secret_key!!")
    JWT_SECRET = "this_is_a_32_characters_secret_key!!"
