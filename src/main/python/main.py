import json
import os
import pathlib
import sys
from pprint import pprint

#from packages.api.Product.gestion_logger import setup_logger_with_rotation

# Ajoute "src/main/python" dans sys.path pour garantir que les modules soient trouvés

# Ajouter le chemin du dossier 'packages' au PYTHONPATH
#if getattr(sys, 'frozen', False):
#   BASE_DIR = sys._MEIPASS
#else:
#   BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(BASE_DIR, 'packages'))
#
#sys.path.insert(0, BASE_DIR)
#os.chdir(BASE_DIR)
#chemin_package = os.path.join(os.path.dirname(__file__), "packages")
#sys.path.append(chemin_package)

# Identifier la base du projet ou l'emplacement temporaire
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
packages_path = os.path.join(base_path, 'packages')
#logger = setup_logger_with_rotation('MAIN_APP', 'main_app.log')
# Ajouter 'packages' à sys.path
#print(f"Syteme path : {sys.path}")
#if packages_path not in sys.path:
#    print("Adding packages path to sys.path")
#    sys.path.append(os.path.normpath(packages_path))
#
## Déboguer le chemin pour vérifier s'il fonctionne
#print(f"Base path utilisé : {base_path}")
#print(f"Chemin des packages : {packages_path}")
#
#if os.path.exists(base_path):
#    print("Contenu du répertoire temporaire (_MEIPASS) :")
#    for root, dirs, files in os.walk(base_path):
#        print(f"Dans {root}:")
#        #logger.info(f"Dans {root}:")
#        for dirname in dirs:
#            print(f"  Dossier : {dirname}")
#            #logger.info(f"Dossier: {dirname}")
#        for filename in files:
#            print(f"  Fichier : {filename}")
#            #logger.info(f"  Fichier : {filename}")
#else:
#    print("Le répertoire temporaire (_MEIPASS) n'existe pas")
#
#try:
#    from packages import __init__
#    print("Importation réussie de __init__.py")
#except ModuleNotFoundError as e:
#    print(f"Erreur lors de l'importation de __init__.py : {e}")
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from fbs_runtime.application_context.PySide6 import ApplicationContext

from packages.leyssare_tech import LeyssareTech
from packages.api.Product.my_config import initialiser_config, create_database,\
    is_postgresql_installed_and_setup, restore_database
from packages.api.Product.gestion_logger import setup_logger_with_rotation
from packages.api.Product.resource_factory import RessourceFactory

if __name__ == '__main__':
    #print(base_path)
    #print(os.getcwd())
    #pprint(os.environ.get("PYTHONPATH", ''))
    #print(sys.path)

    logger = setup_logger_with_rotation('MAIN_APP', 'main_app.log')
    logger.info("Lancement de l'application")
    #logger.info(f"Chemin du dossier de l'application : {BASE_DIR}")
    logger.info(f"Current directory : {os.getcwd()}")

    #On initialise la fonction qui doit se charger de créer le fichier json
    #qui va vontenir les noms de produits dés le premier lancement de programme
    initialiser_config()
    # Utilisation de %USERPROFILE% pour pointer vers le dossier de l'utilisateur courant
    # Utiliser le chemin relatif à partir du script Python

    if is_postgresql_installed_and_setup():
        create_database()
        restore_database()

    logger.info('Demarrage de processus de l appli. ')
    logger.info("--"*20)
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    RessourceFactory.set_contexte(appctxt)
    window = LeyssareTech(ctx=appctxt)
    window.resize(600, 800)
    window.center_window()
    window.show()
    exit_code = appctxt.app.exec()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)