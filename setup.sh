#!/bin/bash
# =====================================
# Script de setup pour Linux/macOS
# Crée un environnement virtuel Python,
# met à jour pip et installe requirements.txt
# =====================================

# Arrêter le script en cas d’erreur
set -e

# Vérifie si Python est installé
if ! command -v python3 &> /dev/null
then
    echo "Python pas installé. Veuillez installer Python 3."
    exit 1
fi

# Crée l'environnement virtuel
echo "Création de l'environnement virtuel."
python3 -m venv .venv

# Active l'environnement
echo "Activation de l'environnement virtuel."
source .venv/bin/activate

# Met à jour pip
echo "Mise à jour de pip"
python -m pip install --upgrade pip

# Installe les dépendances
if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances depuis requirements.txt."
    pip install -r requirements.txt
else
    echo "Aucun requirements.txt trouvé, rien à installer."
fi

echo "Setup terminé avec succès !"