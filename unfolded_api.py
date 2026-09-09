import requests

url_pdb_api = "https://search.rcsb.org/rcsbsearch/v2/query"

requete_idp_corrige = {
    "query": {
        "type": "group",
        "logical_operator": "and",  # Opérateur principal : ET
        "nodes": [
            {
                # Condition 1 : Doit être résolu par RMN
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "exptl.method",
                    "operator": "exact_match",
                    "value": "SOLUTION NMR"
                }
            },
            {
                # Condition 2 : Un sous-groupe avec l'opérateur OU (or)
                "type": "group",
                "logical_operator": "or",
                "nodes": [
                    {
                        "type": "terminal",
                        "service": "full_text",
                        "parameters": {"value": "\"intrinsically disordered\""}
                    },
                    {
                        "type": "terminal",
                        "service": "full_text",
                        "parameters": {"value": "unfolded"}
                    },
                    {
                        "type": "terminal",
                        "service": "full_text",
                        "parameters": {"value": "IDP"}
                    }
                ]
            }
        ]
    },
    "request_options": {"paginate": {"start": 0, "rows": 500}},  # Jusqu'à 500 résultats
    "return_type": "entry"
}

print("Nouvelle recherche avec le filtre OU...")
reponse = requests.post(url_pdb_api, json=requete_idp_corrige)

if reponse.status_code == 200:
    donnees = reponse.json().get("result_set", [])
    liste_id_idp = [res["identifier"] for res in donnees]

    # SAUVEGARDE
    nom_fichier = "ids_proteines_idp.txt"
    with open(nom_fichier, "w") as fichier:
        for identifiant in liste_id_idp:
            fichier.write(f"{identifiant}\n")

    print(f"BINGO ! {len(liste_id_idp)} IDs de protéines désordonnées sauvegardés dans {nom_fichier}.")
else:
    print(f"Erreur API : {reponse.status_code}")