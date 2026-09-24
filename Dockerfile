# Utiliser une image Python officielle légère (version 3.12)
FROM python:3.12-slim

# Définir le dossier de travail à l'intérieur du conteneur
WORKDIR /app

# On copie d'abord uniquement le fichier des dépendances
COPY requirements.txt .

# On installe les dépendances (pynmrstar, pandas, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# On copie ensuite tous les scripts de notre projet dans le conteneur
COPY . .

# Commande par défaut quand le conteneur démarre
CMD ["python", "main.py"]
