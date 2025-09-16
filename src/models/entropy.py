"""
entropy.py
-----------
Ce module calcule l'entropie d'une chaîne (mot de passe, clé ou valeur aléatoire).

Définition :
L'entropie mesure le niveau d'incertitude ou de "désordre".
Plus l'entropie est élevée, plus la valeur est difficile à deviner.
"""
import math
from collections import Counter


def calculate_entropy(value: str) -> float:
    """ calculate_entropy - Calcule l'entropie d'une chaîne de caractères.

    :param value: La chaîne de caractères dont on veut calculer l'entropie.
    :return: L'entropie de la chaîne.
    """
    """
entropy.py
-----------
Ce module calcule l'entropie d'un mot de passe ou d'une chaîne,
avec une vérification préalable des critères de robustesse.

Critères imposés :
- Au moins 12 caractères
- Au moins 1 majuscule
- Au moins 1 minuscule
- Au moins 1 chiffre
- Au moins 1 caractère spécial

Formule utilisée pour l'entropie :
    H = - ∑ (p_i * log2(p_i))
    où p_i est la probabilité d'apparition du caractère i.
"""

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

    # Calculer l'entropie
    counter = Counter(password)
    length = len(password)
    entropy = 0.0

    for count in counter.values():
        p_i = count / length
        entropy -= p_i * math.log2(p_i)

    return {
        "valid": True,
        "errors": [],
        "entropy": entropy
    }
