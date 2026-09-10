import requests
import os

# 1. On charge d'abord les IDPs pour pouvoir les exclure
ids_idp = []
if os.path.exists("ids_proteines_idp.txt"):
    with open("ids_proteines_idp.txt", "r") as f:
        ids_idp = [ligne.strip() for ligne in f.readlines()]
else:
    print("Attention : le fichier ids_proteines_idp.txt est introuvable.")
    print("Lancez d'abord unfolded_api.py pour garantir une bonne exclusion !")

print("Interrogation de l'API PDB pour toutes les protéines RMN...")

url_pdb_api = "https://search.rcsb.org/rcsbsearch/v2/query"
requete = {
    "query": {
        "type": "terminal",
        "service": "text",
        "parameters": {
            "attribute": "exptl.method",
            "operator": "exact_match",
            "value": "SOLUTION NMR"
        }
    },
    "request_options": {"paginate": {"start": 0, "rows": 3000}},  # J'ai monté à 3000 par sécurité
    "return_type": "entry"
}

reponse = requests.post(url_pdb_api, json=requete)

if reponse.status_code == 200:
    toutes_les_rmn = [res["identifier"] for res in reponse.json().get("result_set", [])]
    
    print(f"Trouvé {len(toutes_les_rmn)} protéines RMN au total.")
    
    # === LE FILTRE PYTHON ===
    # On garde la protéine SEULEMENT SI elle n'est pas dans la liste des IDPs
    liste_repliees_pures = [pdb_id for pdb_id in toutes_les_rmn if pdb_id not in ids_idp]
    
    nombre_exclus = len(toutes_les_rmn) - len(liste_repliees_pures)
    print(f"Nettoyage : {nombre_exclus} protéines IDP ont été exclues du groupe contrôle.")
    
    # === SAUVEGARDE ===
    nom_fichier = "ids_proteines_repliees.txt"
    with open(nom_fichier, "w") as fichier:
        for identifiant in liste_repliees_pures:
            fichier.write(f"{identifiant}\n")

    print(f"Succès ! {len(liste_repliees_pures)} IDs purement REPLIÉS sauvegardés dans {nom_fichier}")
else:
    print(f"Erreur API : {reponse.status_code}")