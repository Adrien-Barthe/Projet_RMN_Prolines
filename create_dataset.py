import pynmrstar
import pandas as pd
import time
import os


# 1. La fonction d'extraction
def extraire_prolines(identifiant, type_proteine):
    try:

        entree = pynmrstar.Entry.from_database(str(identifiant))
        boucles_rmn = entree.get_loops_by_category('Atom_chem_shift')

        if len(boucles_rmn) == 0:
            return None

        boucle = boucles_rmn[0]
        df_complet = pd.DataFrame(boucle.data, columns=boucle.tags)

        df_prolines = df_complet[df_complet['Comp_ID'] == 'PRO']
        atomes_squelette = ['CA', 'CB', 'C']
        df_final = df_prolines[df_prolines['Atom_ID'].isin(atomes_squelette)]

        if df_final.empty:
            return None

        df_pivot = df_final.pivot(index='Seq_ID', columns='Atom_ID', values='Val')
        df_pivot.columns = [f"Val_{col}" for col in df_pivot.columns]
        df_pivot.reset_index(inplace=True)

        # Ajout des labels
        df_pivot['Type'] = type_proteine
        df_pivot['ID_Source'] = identifiant  # Renommé car ce sont des ID PDB

        return df_pivot

    except Exception as e:
        # On affiche la VRAIE erreur pour savoir si c'est le réseau qui a coupé ou si la donnée n'existe pas
        print(f"Erreur pour l'ID {identifiant} : {e}")
        return None


# 2. Fonction pour lire, NETTOYER et SÉPARER les fichiers textes
def charger_ids(nom_fichier):
    if not os.path.exists(nom_fichier):
        print(f"Attention: {nom_fichier} introuvable.")
        return []

    with open(nom_fichier, "r") as fichier:
        ids_propres = [ligne.strip() for ligne in fichier.readlines() if ligne.strip()]
        
    # On enlève les doublons
    return list(set(ids_propres))


def build_dataset():
    nom_csv = "dataset_prolines_complet.csv"
    nom_vides = "ids_vides.txt"

    # 1. On charge les listes TRADUITES générées à l'étape précédente
    liste_id_idp = charger_ids("ids_bmrb_idp.txt")
    liste_id_repliees = charger_ids("ids_bmrb_repliees.txt")
    
    # === LA MÉMOIRE DU SCRIPT (CHECKPOINTING) ===
    ids_deja_vus = set()
    
    # A. On mémorise les protéines qui sont déjà dans le CSV
    if os.path.exists(nom_csv):
        df_existant = pd.read_csv(nom_csv)
        if 'ID_Source' in df_existant.columns:
            ids_deja_vus.update(df_existant['ID_Source'].astype(str).unique())
            
    # B. On mémorise les protéines qu'on sait déjà être vides (échecs)
    if os.path.exists(nom_vides):
        with open(nom_vides, "r") as f:
            ids_deja_vus.update([ligne.strip() for ligne in f.readlines()])
            
    # 3. On filtre nos listes pour retirer les "déjà-vus"
    liste_id_idp = [id for id in liste_id_idp if str(id) not in ids_deja_vus]
    liste_id_repliees = [id for id in liste_id_repliees if str(id) not in ids_deja_vus]

    print(f"Après vérification du cache, il reste à télécharger : {len(liste_id_idp)} IDPs et {len(liste_id_repliees)} Repliées.")

    # 4. Le moteur de téléchargement en continu
    def traiter_et_sauvegarder(liste_ids, type_prot):
        for identifiant in liste_ids:
            print(f"Traitement de {identifiant} ({type_prot})...")
            df = extraire_prolines(identifiant, type_prot)
            
            if df is not None:
                # On vérifie d'abord que l'expérience RMN a bien mesuré le C, CA et CB
                colonnes_requises = {'Val_C', 'Val_CA', 'Val_CB'}
                if colonnes_requises.issubset(df.columns):
                    # On nettoie la protéine
                    df_propre = df.dropna(subset=list(colonnes_requises))
                    if not df_propre.empty:
                        # SAUVEGARDE SÉCURISÉE EN TEMPS RÉEL (mode = 'a' pour Append/Ajout)
                        entete = not os.path.exists(nom_csv)
                        df_propre.to_csv(nom_csv, mode='a', header=entete, index=False)
                    else:
                        # La protéine avait des données, mais aucune parfaite après nettoyage
                        with open(nom_vides, "a") as f:
                            f.write(f"{identifiant}\n")
                else:
                    # S'il manque totalement la colonne C, CA ou CB, la protéine est inutile
                    with open(nom_vides, "a") as f:
                        f.write(f"{identifiant}\n")
            else:
                # La protéine ne contenait pas du tout de données RMN utilisables
                with open(nom_vides, "a") as f:
                    f.write(f"{identifiant}\n")
                    
            time.sleep(0.5) # On ne spamme pas le serveur

    # 5. On lance le moteur sur nos deux listes filtrées
    print("\nTéléchargement des protéines désordonnées (IDP)...")
    traiter_et_sauvegarder(liste_id_idp, "IDP")
    
    print("\nTéléchargement des protéines repliées...")
    traiter_et_sauvegarder(liste_id_repliees, "REPLIEE")

    print("\n--- TÉLÉCHARGEMENT SÉCURISÉ TERMINÉ ---")
    
    # 6. Bilan final pour le main.py
    if os.path.exists(nom_csv):
        df_final = pd.read_csv(nom_csv)
        print(f"Nombre total de prolines PARFAITES dans la base : {len(df_final)}")
        return True
    else:
        print("Aucune donnée n'a pu être extraite globalement.")
        return False

if __name__ == "__main__":
    build_dataset()