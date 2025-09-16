<#
=====================================
Script de setup pour Windows PowerShell
Crée un environnement virtuel Python,
met à jour pip et installe requirements.txt
=====================================
#>

# Stoppe le script en cas d’erreur
$ErrorActionPreference = "Stop"

# Vérifie si Python est installé
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python n'est pas installé. Installez-le d'abord."
    exit 1
}

# Crée l'environnement virtuel s'il n'existe pas déjà
if (-not (Test-Path ".venv")) {
    Write-Output "Création de l'environnement virtuel."
    python -m venv .venv
}

# Active l'environnement
Write-Output "Activation de l'environnement virtuel."
.venv\Scripts\Activate.ps1

# Met à jour pip
Write-Output "⬆Mise à jour de pip."
python.exe -m pip install --upgrade pip

# Installe les dépendances
if (Test-Path "requirements.txt") {
    Write-Output "Installation des dépendances depuis requirements.txt."
    pip install -r requirements.txt
} else {
    Write-Warning "Aucun requirements.txt trouvé, rien à installer."
}

Write-Output "Setup terminé avec succès !"