import os

import pytest

from config.db import db


@pytest.fixture(scope="session")
def test_db_uri(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    return f"sqlite:///{db_path.as_posix()}"


@pytest.fixture(scope="session")
def app(test_db_uri):
    os.environ["DATABASE_URL"] = str(test_db_uri)
    os.environ.setdefault("ENVIRONMENT", "testing")

    from app import create_app

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_database(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()
