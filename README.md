# Analyse RMN des Prolines (IDP vs Repliées)

## Objectif
Obtenir des informations sur la structure locale du squelette peptidique, à l'aide des déplacements chimiques RMN (C, Cα, Cβ) des prolines pour différencier les protéines intrinsèquement désordonnées (IDP) des protéines repliées.

## Structure du projet
- `main.py` : Chef d'orchestre qui lance automatiquement toutes les étapes du pipeline.
- `unfolded_api.py` : Télécharge les ID PDB des protéines désordonnées (groupe d'étude).
- `folded_api.py` : Télécharge les ID PDB des protéines repliées (groupe contrôle) en excluant rigoureusement les IDP.
- `id_mapping.py` : Fait le lien de traduction entre les identifiants PDB et BMRB.
- `create_dataset.py` : Extrait, filtre (uniquement les prolines CA, CB, C) et nettoie les données via l'API BMRB.
- `dataset_prolines_complet.csv` : Le jeu de données final, propre et prêt pour le Machine Learning (généré localement, ignoré par Git).

## Utilisation (Recommandée avec Docker 🐳)
L'utilisation de Docker garantit un environnement de recherche reproductible et résout les problèmes d'installation des dépendances scientifiques (comme `pynmrstar`).

1. **Construire l'image Docker** (à ne faire qu'une seule fois) :
   ```bash
   docker build -t projet-rmn .
   ```
2. **Lancer le pipeline complet** :
   ```bash
   docker run -it -v $(pwd):/app:Z projet-rmn
   ```
   *Le paramètre de volume `-v` permet au conteneur de sauvegarder les fichiers de résultats (`.txt` et `.csv`) directement sur votre disque dur physique.*

## Utilisation (Environnement local classique)
1. Cloner ce dépôt
2. Créer un environnement virtuel : `python -m venv .venv`
3. Activer l'environnement (`source .venv/bin/activate` sous Linux/Mac ou `.venv\Scripts\activate` sous Windows)
4. Installer les dépendances : `pip install -r requirements.txt`
5. Lancer le pipeline : `python main.py`