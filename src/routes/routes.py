from flask import Blueprint, request, jsonify, make_response
from models.entropy import calculate_entropy
from models.user import User
from config.db import db
from Crypto.Cipher import AES
import jwt
import datetime

from config.config import Config


bp = Blueprint("routes", __name__)


def pad(data: bytes) -> bytes:
    """Ajoute du padding PKCS7 pour AES (bloc de 16 octets)."""
    padding_len = 16 - len(data) % 16
    return data + bytes([padding_len]) * padding_len


def unpad(data: bytes) -> bytes:
    """Retire le padding PKCS7."""
    if not data:
        return data
    padding_len = data[-1]
    if padding_len < 1 or padding_len > 16:
        raise ValueError("Invalid padding length")
    return data[:-padding_len]


@bp.route("/login", methods=["POST"])
def entropy_login():
    """
    Endpoint /login
    ---------------
    Reçoit username + password,
    chiffre le mot de passe comme dans /register,
    compare avec celui en BDD,
    puis génère un JWT contenant le rôle.

    Expects JSON: { "username": "john", "password": "Password123!" }
    """
    data = request.get_json()

    # Vérification des champs requis
    if not data or "username" not in data or "password" not in data:
        return jsonify({
            "error": "Champs 'username' et 'password' requis"
        }), 400

    username, password = data["username"], data["password"]

    # Récupération de l'utilisateur
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Utilisateur ou mot de passe incorrect"}), 401

    # Chiffrement AES (même méthode que register)
    key = Config.AES_KEY.encode("utf-8")[:32]
    cipher = AES.new(key, AES.MODE_CBC, iv=b"0123456789abcdef")
    encrypted_pwd = cipher.encrypt(pad(password.encode("utf-8")))

    # Vérification du mot de passe chiffré
    if encrypted_pwd != user.password_encrypted:
        return jsonify({"error": "Utilisateur ou mot de passe incorrect"}), 401

    # Génération d'un JWT avec le rôle
    payload = {
        "sub": user.username,
        "role": getattr(user, "role", "user"),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    # Réponse avec token et rôle
    response = make_response(jsonify({
        "message": "Connexion réussie",
        "username": user.username,
        "role": payload["role"],
        "token": token,
    }), 200)

    # Enregistrement du token dans un cookie HttpOnly
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=3600,
    )

    return response


@bp.route("/register", methods=["POST"])
def entropy_register():
    """
    Endpoint /register
    ------------------
    Reçoit un mot de passe, vérifie sa validité,
    calcule son entropie et sa redondance
    puis enregistre l'utilisateur si valide.

    Expects JSON: { "username": "john", "password": "Password123!" }
    """
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Champs 'username' et 'password' requis"}), 400

    username, password = data["username"], data["password"]

    # Calcul des métriques
    result = calculate_entropy(username, password)

    # Gestion si invalide
    if not result["valid"]:
        return jsonify({
            "value": [username],
            "valid": False,
            "errors": result["errors"],
            "entropy_bits": None,
            "redundancy_percent": None,
            "components": result["components"],
        }), 400

    # Chiffrement AES
    key = Config.AES_KEY.encode("utf-8")[:32]
    cipher = AES.new(key, AES.MODE_CBC, iv=b"0123456789abcdef")
    encrypted_pwd = cipher.encrypt(pad(password.encode("utf-8")))

    # Vérifie si l'utilisateur existe déjà
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Utilisateur déjà existant"}), 400

    # Sauvegarde en base (stocke aussi l'entropie)
    new_user = User(
        username=username,
        password_encrypted=encrypted_pwd,
        entropy=result["entropy_bits"],  # champ adapté
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "value": [username, password],
        "valid": True,
        "errors": [],
        "entropy_bits": result["entropy_bits"],
        "redundancy_percent": result["redundancy_percent"],
        "components": result["components"],  # R1, R2, R3
    }), 200


@bp.route("/dashboard", methods=["GET"])
def entropy_dashboard():
    """
    Endpoint /dashboard
    -------------------
    Accessible uniquement par un utilisateur avec le rôle "admin".
    Retourne la liste de tous les utilisateurs.
    """
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"error": "Accès refusé : token manquant"}), 401

    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Session expirée"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token invalide"}), 401

    if payload.get("role") != "admin":
        return jsonify({
            "error": "Accès interdit : vous n'avez pas les droits"
        }), 403

    users = User.query.all()
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "entropy": user.entropy,
            "role": getattr(user, "role", "user"),
        }
        for user in users
    ]

    return jsonify({
        "message": "Dashboard admin",
        "users": users_data,
    }), 200


@bp.route("/update-role", methods=["POST"])
def update_role():
    """
    Endpoint /update-role
    ---------------------
    Permet à un admin de modifier le rôle d'un utilisateur.

    Expects JSON: { "username": "john", "new_role": "admin" }
    """
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"error": "Accès refusé : token manquant"}), 401

    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Session expirée"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token invalide"}), 401

    if payload.get("role") != "admin":
        return jsonify({
            "error": "Accès interdit : droits insuffisants"
        }), 403

    data = request.get_json()
    if not data or "username" not in data or "new_role" not in data:
        return jsonify({
            "error": "Champs 'username' et 'new_role' requis"
        }), 400

    username = data["username"]
    new_role = data["new_role"]

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user.role = new_role
    db.session.commit()

    return jsonify({
        "message": f"Le rôle de {username} a été mis à jour en '{new_role}'"
    }), 200


@bp.route("/logout", methods=["POST"])
def logout():
    """
    Endpoint /logout
    ----------------
    Supprime le cookie JWT afin de déconnecter l'utilisateur.
    """
    response = make_response(jsonify({
        "message": "Déconnexion réussie"
    }), 200)

    response.set_cookie(
        "access_token",
        "",
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=0,
    )

    return response
