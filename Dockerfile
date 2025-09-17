# Utiliser une image Python légère
FROM python:3.11-slim

# Copier les fichiers de dépendances et installer
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier le reste de l'application
COPY ./src ./src

# Exposer le port sur lequel Flask tourne
EXPOSE 5000

# Variables d'environnement pour Flask
ENV FLASK_ENV=production

# Définir le répertoire de travail pour exécuter app.py
WORKDIR /app/src

# Lancer l'application avec python app.py
CMD ["python", "app.py"]
