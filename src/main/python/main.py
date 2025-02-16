import logging
import os
import pathlib
import subprocess
import sys
# Ajoute "src/main/python" dans sys.path pour garantir que les modules soient trouvés
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from fbs_runtime.application_context.PySide6 import ApplicationContext

from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
import json

from packages.leyssare_tech import LeyssareTech
from packages.api.Product.my_config import initialiser_config, create_database,\
    is_postgresql_installed_and_setup, restore_database

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Lancement de l'application")
    #On initialise la fonction qui doit se charger de créer le fichier json
    #qui va vontenir les noms de produits dés le premier lancement de programme
    initialiser_config()
    # Utilisation de %USERPROFILE% pour pointer vers le dossier de l'utilisateur courant
    # Utiliser le chemin relatif à partir du script Python

    #if not is_postgres_installed():
    #   logging.info('execution du fichier .bat')
    #   script_path = str(pathlib.Path.cwd().parent, "resources/postgres_installateur/", "postgres_installateur/install_postgresql.bat")
    #   scipt_install_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "postgres_installateur", "install_postgresql.bat")
    #   print(f"rep actu", scipt_install_path)

       #subprocess.run([scipt_install_path], shell=True)
       #subprocess.run([scipt_install_path], shell=True)
       #logging.info('execution du fichier .bat terminée')
    #On lance le processus de création de base données
    #if not database_exists():
    #    logging.info('Creation de la base de donnée')
    #    create_database()
    #    logging.info('Creation de la base de donnée terminée')
    if is_postgresql_installed_and_setup():
        create_database()
        restore_database()

    logging.info('Demarrage de processus de l appli. ')
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = LeyssareTech(ctx=appctxt)
    window.resize(600, 800)
    window.center_window()
    window.show()
    printer = QPrinter()
    #window.handlerPrint(printer)
    window.btn_scannen.click()
    exit_code = appctxt.app.exec()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)