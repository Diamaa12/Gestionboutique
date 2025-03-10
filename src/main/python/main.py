import os
import sys
# Ajoute "src/main/python" dans sys.path pour garantir que les modules soient trouvés
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from fbs_runtime.application_context.PySide6 import ApplicationContext

from packages.leyssare_tech import LeyssareTech
from packages.api.Product.my_config import initialiser_config, create_database,\
    is_postgresql_installed_and_setup, restore_database
from packages.api.Product.gestion_logger import setup_logger_with_rotation

if __name__ == '__main__':
    logguer = setup_logger_with_rotation('MAIN_APP', 'main_app.log')
    logguer.info("Lancement de l'application")
    #On initialise la fonction qui doit se charger de créer le fichier json
    #qui va vontenir les noms de produits dés le premier lancement de programme
    initialiser_config()
    # Utilisation de %USERPROFILE% pour pointer vers le dossier de l'utilisateur courant
    # Utiliser le chemin relatif à partir du script Python

    if is_postgresql_installed_and_setup():
        create_database()
        restore_database()

    logguer.info('Demarrage de processus de l appli. ')
    logguer.info("--"*20)
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = LeyssareTech(ctx=appctxt)
    window.resize(600, 800)
    window.center_window()
    window.show()
    exit_code = appctxt.app.exec()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)