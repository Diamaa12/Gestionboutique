import json
from pathlib import Path
from fbs import path, init


def initialiser_config():
    """Initialiser la configuration de l'application."""
    # Déterminer le répertoire du projet (remplacez-le par le chemin approprié)
    project_dir = str(Path(__file__).parent)  # Par défaut on prend le répertoire actuel
    init(project_dir)  # Initialiser avec le bon répertoire
    print(project_dir)
    # Chemin du répertoire d'installation de l'application
    repertoire_installation = path("base")  # "base" correspond au répertoire d'installation

    # Création du répertoire si il n'existe pas
    repertoire_installation = Path(repertoire_installation)
    repertoire_installation.mkdir(parents=True, exist_ok=True)
    print(repertoire_installation)
    # Chemin du fichier JSON
    fichier_json = repertoire_installation / 'products.json'
    print(f"Chemin du fichier JSON : {fichier_json}")

    # Vérifier si le fichier JSON existe, sinon le créer avec des données par défaut
    if not fichier_json.exists():
        print(f"Création du fichier JSON dans {fichier_json}")
        donnees_par_defaut = ['']
        with fichier_json.open(mode='w', encoding='utf-8') as fichier:
            json.dump(donnees_par_defaut, fichier, indent=4, ensure_ascii=False)
    else:
        print("Le fichier JSON existe déjà, aucune création nécessaire.")


if __name__ == '__main__':
    # Initialiser la configuration
    initialiser_config()
