from flask import Blueprint

bp = Blueprint("routes", __name__)

@bp.route("/entropy", methods=["POST"])
def entropy_endpoint():
    # TODO: Implémenter la logique pour calculer l'entropie
    return ""