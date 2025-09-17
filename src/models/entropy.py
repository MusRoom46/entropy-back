import math
import re
from collections import Counter


def calculate_entropy(username: str, password: str) -> dict:
    """
    Vérifie la robustesse du mot de passe et calcule son entropie.

    Paramètres :
        password (str) : mot de passe à évaluer.

    Retour :
        dict :
        - "valid" (bool) : indique si le mot de passe respecte les critères
        - "errors" (list[str]) : liste des critères non respectés
        - "entropy" (float | None) : entropie en bits si valide, sinon None
    """

    errors = []

    # Vérifie la longueur
    if len(password) < 12:
        errors.append("Le mot de passe doit contenir au moins 12 caractères.")

    # Vérifie présence d'une majuscule
    if not re.search(r"[A-Z]", password):
        errors.append("Le mot de passe doit contenir au moins une majuscule.")

    # Vérifie présence d'une minuscule
    if not re.search(r"[a-z]", password):
        errors.append("Le mot de passe doit contenir au moins une minuscule.")

    # Vérifie présence d'un chiffre
    if not re.search(r"[0-9]", password):
        errors.append("Le mot de passe doit contenir au moins un chiffre.")

    # Vérifie présence d'un caractère spécial
    if not re.search(r"[^a-zA-Z0-9]", password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial.")

    # Si critères non respectés, retourne les erreurs
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "entropy": None
        }

     # Comptage des caractères uniques par catégorie
    lower_used = len(set(c for c in password if c.islower())) * math.log2(26)
    upper_used = len(set(c for c in password if c.isupper())) * math.log2(26)
    digits_used = len(set(c for c in password if c.isdigit())) * math.log2(10)
    symbols_used = len(set(c for c in password if c in string.punctuation)) * math.log2(33)

    # Alphabet effectif = somme des caractères uniques utilisés dans chaque catégorie
    alphabet_size = lower_used + upper_used + digits_used + symbols_used
    length = len(password)

    # Calcul de l'entropie
    entropy = length * math.log2(alphabet_size) if alphabet_size > 0 else 0

    return {
        "valid": True,
        "errors": [],
        "entropy": entropy
    }
