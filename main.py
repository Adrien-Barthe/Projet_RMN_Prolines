import time
import sys
import argparse

from unfolded_api import run_unfolded_api
from folded_api import run_folded_api
from id_mapping import run_id_mapping
from create_dataset import build_dataset

def main():
    print("="*50)
    print("DÉMARRAGE DU PIPELINE PROLINES RMN ")
    print("="*50)

    # ÉTAPE 1
    print("\n--- [ÉTAPE 1/4] Recherche des IDPs ---")
    if not run_unfolded_api():
        print("Échec lors de la récupération des IDPs. Arrêt du pipeline.")
        sys.exit(1)

    # ÉTAPE 2
    print("\n--- [ÉTAPE 2/4] Recherche des protéines repliées (contrôle) ---")
    if not run_folded_api():
        print("Échec lors de la récupération des protéines repliées. Arrêt du pipeline.")
        sys.exit(1)

    # ÉTAPE 3
    print("\n--- [ÉTAPE 3/4] Traduction PDB -> BMRB ---")
    if not run_id_mapping():
        print("Échec lors de la traduction des identifiants. Arrêt du pipeline.")
        sys.exit(1)

    # ÉTAPE 4
    print("\n--- [ÉTAPE 4/4] Extraction des prolines depuis la BMRB ---")
    # On chronomètre cette étape car elle est longue
    debut = time.time()
    if not build_dataset():
        print("Échec lors de la création du dataset final.")
        sys.exit(1)
    fin = time.time()
    
    duree = fin - debut
    print("="*50)
    print(f"PIPELINE TERMINÉ AVEC SUCCÈS ! ")
    print(f"Temps de téléchargement BMRB : {duree:.2f} secondes.")
    print("="*50)

if __name__ == "__main__":
    main()
