import json
import os
from pathlib import Path


def initialiser_config():
    """Initialiser la configuration de l'application."""
    # Obtenir le dossier Documents de l'utilisateur courant
    dossier_documents = Path(os.getenv("PROGRAMDATA")) / "BBLTech/PRODUCT_JSON"  # Vous pouvez changer 'MonApplication' selon vos besoins
    dossier_documents.mkdir(parents=True, exist_ok=True)  # Créer le dossier si nécessaire
    print(f"Répertoire de configuration : {dossier_documents}")

    # Chemin du fichier JSON
    fichier_json = dossier_documents / 'products.json'
    print(f"Chemin du fichier JSON : {fichier_json}")

    # Vérifier si le fichier JSON existe, sinon le créer avec des données par défaut
    if not fichier_json.exists():
        try:
            print(f"Création du fichier JSON dans {fichier_json}")
            donnees_par_defaut = ['']
            with fichier_json.open(mode='w', encoding='utf-8') as fichier:
                json.dump(donnees_par_defaut, fichier, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la création du fichier JSON : {e}")
    else:
        print("Le fichier JSON existe déjà, aucune création nécessaire.")


if __name__ == '__main__':
    initialiser_config()
