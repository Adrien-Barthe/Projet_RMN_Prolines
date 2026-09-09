import requests

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
    "request_options": {"paginate": {"start": 0, "rows": 2500}},  # Récupérons 2500 ID !
    "return_type": "entry"
}

reponse = requests.post(url_pdb_api, json=requete)

if reponse.status_code == 200:
    liste_id = [res["identifier"] for res in reponse.json().get("result_set", [])]

    nom_fichier = "ids_proteines_repliees.txt"
    with open(nom_fichier, "w") as fichier:
        for identifiant in liste_id:
            fichier.write(f"{identifiant}\n")  # \n pour passer à la ligne

    print(f"Succès ! {len(liste_id)} ID sauvegardés dans {nom_fichier}")
else:
    print(f"Erreur API : {reponse.status_code}")