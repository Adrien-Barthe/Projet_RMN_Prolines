import requests
import os


def charger_ids(nom_fichier):
    if not os.path.exists(nom_fichier):
        return []
    with open(nom_fichier, "r") as fichier:
        return [ligne.strip().upper() for ligne in fichier.readlines() if ligne.strip()]


def run_id_mapping():
    print("1. Lecture de vos listes PDB...")
    pdb_idp = charger_ids("ids_proteines_idp.txt")
    pdb_repliees = charger_ids("ids_proteines_repliees.txt")

    print("2. Interrogation de l'API BMRB pour le dictionnaire officiel...")
    url_api_mapping = "https://api.bmrb.io/v2/mappings/pdb/bmrb"
    reponse = requests.get(url_api_mapping)

    if reponse.status_code == 200:
        print(" ---> Dictionnaire téléchargé avec succès !")
        mapping_brut = reponse.json()

        mapping_propre = {}

        # On parcourt la liste renvoyée par l'API
        for element in mapping_brut:
            v1, v2 = "", ""

            # Format 1 : Le format standard API v2 [{"pdb_id": "1ABC", "bmrb_ids": ["1234", "5678"]}]
            if isinstance(element, dict) and "pdb_id" in element and "bmrb_ids" in element:
                pdb_id = str(element["pdb_id"]).upper()
                for b_id in element["bmrb_ids"]:
                    if pdb_id not in mapping_propre:
                        mapping_propre[pdb_id] = []
                    mapping_propre[pdb_id].append(str(b_id))
                continue
                
            # Format 2 (Legacy/Secours) : Liste de valeurs ["1ABC", "1234"]
            elif isinstance(element, list) and len(element) >= 2:
                v1, v2 = str(element[0]).upper(), str(element[1])
                
                if v1.isdigit() and not v2.isdigit():
                    pdb_id, bmrb_id = v2.upper(), v1
                elif v2.isdigit() and not v1.isdigit():
                    pdb_id, bmrb_id = v1.upper(), v2
                else:
                    continue
                    
                if pdb_id not in mapping_propre:
                    mapping_propre[pdb_id] = []
                mapping_propre[pdb_id].append(bmrb_id)

        print("3. Traduction en cours...")

        bmrb_idp = []
        for pdb in pdb_idp:
            pdb = pdb.upper()
            if pdb in mapping_propre:
                bmrb_idp.extend(mapping_propre[pdb])

        bmrb_repliees = []
        for pdb in pdb_repliees:
            pdb = pdb.upper()
            if pdb in mapping_propre:
                bmrb_repliees.extend(mapping_propre[pdb])

        # On supprime les doublons éventuels
        bmrb_idp = list(set(bmrb_idp))
        bmrb_repliees = list(set(bmrb_repliees))

        print(f"\n--- BILAN DE LA TRADUCTION ---")
        print(f"IDP : {len(bmrb_idp)} vrais IDs BMRB trouvés !")
        print(f"Repliées : {len(bmrb_repliees)} vrais IDs BMRB trouvés !")

        # 4. Sauvegarde dans de nouveaux fichiers
        with open("ids_bmrb_idp.txt", "w") as f:
            f.write("\n".join(bmrb_idp))

        with open("ids_bmrb_repliees.txt", "w") as f:
            f.write("\n".join(bmrb_repliees))

        print("Nouveaux fichiers de traduction sauvegardés !")
        return True
    else:
        print(f"Erreur critique avec l'API : Code {reponse.status_code}")
        return False

if __name__ == "__main__":
    run_id_mapping()