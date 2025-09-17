from flask import Blueprint, request, jsonify
from models.entropy import calculate_entropy
from models.user import User
from config.db import db
from Crypto.Cipher import AES
import base64
import os

from config.config import Config

bp = Blueprint("routes", __name__)

def pad(data: bytes) -> bytes:
    """Ajoute du padding PKCS7 pour AES (bloc de 16 octets)."""
    padding_len = 16 - len(data) % 16
    return data + bytes([padding_len]) * padding_len

@bp.route("/entropy", methods=["POST"])
def entropy_endpoint():
    # TODO: Implémenter la logique pour calculer l'entropie
    return ""

@bp.route("/login", methods=["POST"])
def entropy_login():
    # TODO: Implémenter la logique pour le login
    return ""

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
    cipher = AES.new(Config.AES_KEY.encode("utf-8")[:32], AES.MODE_CBC)
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