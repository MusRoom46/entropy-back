from flask import Blueprint

bp = Blueprint("routes", __name__)

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
    # TODO: Implémenter la logique pour le register
    return ""

@bp.route("/profile", methods=["GET"])
def entropy_profile():
    # TODO: Implémenter la logique pour le profile
    return ""