import os

class Config:
    # URI de connexion PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://entropy_user:entropy_pass@localhost:5432/entropy_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète pour AES (16, 24 ou 32 octets)
    AES_KEY = os.getenv("AES_KEY", "this_is_a_32_characters_secret_key!!")
    JWT_SECRET = "this_is_a_32_characters_secret_key!!"
