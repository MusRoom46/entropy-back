from flask import Blueprint, request, jsonify, make_response
from models.entropy import calculate_entropy
from models.user import User
from config.db import db
from Crypto.Cipher import AES
import jwt
import datetime
import hmac

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
    """
    data = request.get_json()

    # Vérification des champs requis
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Champs 'username' et 'password' requis"}), 400

    username, password = data["username"], data["password"]

    # Récupération de l'utilisateur
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Utilisateur inexistant"}), 401

    # Chiffrement AES (même méthode que register)
    key = Config.AES_KEY.encode("utf-8")[:32]
    cipher = AES.new(key, AES.MODE_CBC, iv=b"0123456789abcdef")
    encrypted_pwd = cipher.encrypt(pad(password.encode("utf-8")))

    # Vérification du mot de passe chiffré
    if encrypted_pwd != user.password_encrypted:
        return jsonify({"error": "Mot de passe incorrect"}), 401

    # Génération d’un JWT avec le rôle
    payload = {
        "sub": user.username,
        "role": getattr(user, "role", "user"),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    # Réponse avec token et rôle
    response = make_response(jsonify({
        "message": "Connexion réussie",
        "username": user.username,
        "role": payload["role"],
        "token": token
    }), 200)

    # Enregistrement du token dans un cookie HttpOnly (optionnel mais recommandé)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=3600
    )

    return response

@bp.route("/register", methods=["POST"])
def entropy_register():
    """
    Endpoint /register
    ------------------
    Reçoit un mot de passe, vérifie sa validité
    et calcule son entropie si les critères sont respectés.

    - Si le champ "username" ou "password" sont absents → erreur 400
    - Si le mot de passe est invalide → retour avec erreurs
    - Si valide → retour avec l'entropie
    """
    # Récupère le JSON envoyé par le client
    data = request.get_json()

    # Vérifie que la clé "value" existe dans le JSON
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Champ 'value' manquant"}), 400

    username, password = data["username"], data["password"]
    
    # Calcule l'entropie avec la fonction définie dans entropy.py
    result = calculate_entropy(username, password)

    # Si le mot de passe est invalide → renvoyer les erreurs
    if not result["valid"]:
        return jsonify({
            "value": [username, password],
            "valid": False,
            "errors": result["errors"],
            "entropy": None
        }), 400
    
    # Chiffrement AES sur 32 octets
    key = Config.AES_KEY.encode("utf-8")[:32]
    cipher = AES.new(key, AES.MODE_CBC, iv=b"0123456789abcdef")
    encrypted_pwd = cipher.encrypt(pad(password.encode("utf-8")))

    # Vérification si l'utilisateur existe déjà
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({"error": "Utilisateur déjà existant"}), 400

    # Stockage DB
    new_user = User(
        username=username,
        password_encrypted=encrypted_pwd,
        entropy=result["entropy"]
    )
    db.session.add(new_user)
    db.session.commit()

    # Si valide → renvoyer la valeur de l'entropie
    return jsonify({
        "value": [username, password],
        "valid": True,
        "errors": [],
        "entropy": result["entropy"]
    }), 200

@bp.route("/profile", methods=["GET"])
def entropy_profile():
    # TODO: Implémenter la logique pour le profile
    return ""