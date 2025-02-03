import os
import sys
# Ajoute "src/main/python" dans sys.path pour garantir que les modules soient trouvés
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from fbs_runtime.application_context.PySide6 import ApplicationContext

from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
import json

from packages.leyssare_tech import LeyssareTech
from packages.api.Product.my_config import initialiser_config



if __name__ == '__main__':
    #On initialise la fonction qui doit se charger de créer le fichier json
    #qui va vontenir les noms de produits dés le premier lancement de programme
    initialiser_config()
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = LeyssareTech(ctx=appctxt)
    window.resize(700, 900)
    window.show()
    printer = QPrinter()
    #window.handlerPrint(printer)
    window.btn_scannen.click()
    exit_code = appctxt.app.exec()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)