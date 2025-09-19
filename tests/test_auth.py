from flask import Response

from config.db import db
from models.user import User


def _register_user(client, username: str, password: str) -> Response:
    return client.post(
        "/register",
        json={"username": username, "password": password},
    )


def _login_user(client, username: str, password: str) -> Response:
    return client.post(
        "/login",
        json={"username": username, "password": password},
    )


def test_dashboard_requires_bearer_or_cookie(client):
    response = client.get("/dashboard")

    assert response.status_code == 401
    body = response.get_json()
    assert body["error"].endswith("token manquant")


def test_dashboard_accepts_authorization_header(client, app):
    username = "admin_user"
    password = "ValidPassword1!"

    register_response = _register_user(client, username, password)
    assert register_response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        user.role = "admin"
        db.session.commit()

    login_response = _login_user(client, username, password)
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Dashboard admin"
    assert any(user_data["username"] == username for user_data in data["users"])