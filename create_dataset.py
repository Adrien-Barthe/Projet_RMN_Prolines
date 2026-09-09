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
        # Ignore les erreurs (ex: si l'ID PDB n'a finalement pas d'équivalent BMRB)
        print(f"Erreur/Pas de données RMN pour l'ID {identifiant}")
        return None


# 2. Fonction pour lire, NETTOYER et SÉPARER les fichiers textes
def charger_ids(nom_fichier):
    if not os.path.exists(nom_fichier):
        print(f"Attention: {nom_fichier} introuvable.")
        return []

    ids_propres = []
    with open(nom_fichier, "r") as fichier:
        for ligne in fichier.readlines():
            id_brut = ligne.strip()

            # 1. On nettoie les ids
            id_nettoye = id_brut.replace("[", "").replace("]", "").replace("'", "").replace('"', "")

            # 2. On découpe la ligne à chaque virgule
            if id_nettoye:
                pour_chaque_numero = id_nettoye.split(",")

                for numero in pour_chaque_numero:
                    numero_propre = numero.strip()
                    if numero_propre:
                        ids_propres.append(numero_propre)

    # 3. On enlève les éventuels doublons pour ne pas télécharger deux fois la même chose
    return list(set(ids_propres))


# On charge les listes TRADUITES générées à l'étape précédente
liste_id_idp = charger_ids("ids_bmrb_idp.txt")
liste_id_repliees = charger_ids("ids_bmrb_repliees.txt")

print(f"Prêt à traiter : {len(liste_id_idp)} IDPs et {len(liste_id_repliees)} Repliées.")

# 3. La boucle de téléchargement
tous_les_tableaux = []

print("\nTéléchargement des protéines désordonnées (IDP)...")
for identifiant in liste_id_idp:
    print(f"Traitement de {identifiant}...")
    df = extraire_prolines(identifiant, "IDP")
    if df is not None:
        tous_les_tableaux.append(df)
    time.sleep(0.5)

print("\nTéléchargement des protéines repliées...")
for identifiant in liste_id_repliees:
    print(f"Traitement de {identifiant}...")
    df = extraire_prolines(identifiant, "REPLIEE")
    if df is not None:
        tous_les_tableaux.append(df)
    time.sleep(0.5)

#Nettoyage dataset
if tous_les_tableaux:
    dataframe_final = pd.concat(tous_les_tableaux, ignore_index=True)

    print("\n--- NETTOYAGE DU TABLEAU ---")
    taille_avant = len(dataframe_final)

    # Suppression des prolines incomplètes
    dataframe_final = dataframe_final.dropna(subset=['Val_C', 'Val_CA', 'Val_CB'])

    taille_apres = len(dataframe_final)
    print(f"Prolines incomplètes supprimées : {taille_avant - taille_apres}")

    print("\n--- TABLEAU GÉANT CRÉÉ AVEC SUCCÈS ---")
    print(f"Nombre total de prolines PARFAITES : {taille_apres}")

    dataframe_final.to_csv("dataset_prolines_complet.csv", index=False)
    print("Données sauvegardées dans 'dataset_prolines_complet.csv'")
else:
    print("Aucune donnée n'a pu être extraite.")