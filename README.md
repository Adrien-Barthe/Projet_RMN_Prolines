# Analyse RMN des Prolines (IDP vs Repliées)

## Objectif
Obtenir des informations sur la structure locale du squelette peptidique, à l'aide des déplacements chimiques RMN (C, Cα, Cβ) des prolines.

## Installation
1. Cloner ce dépôt
2. Créer un environnement virtuel : `python -m venv .venv`
3. Installer les dépendances : `pip install -r requirements.txt`

## Structure du projet
- `folded_api.py` : Télécharge les ID PDB "repliées".
- `unfolded_api.py` : Télécharge les ID PDB "désordonnées".
- `id_mapping.py` : Fait le lien entre les ID PDB et BMRB.
- `create_dataset.py` : Extrait et nettoie les données via l'API BMRB.
- `dataset_prolines_complet.csv` : Le jeu de données final propre.