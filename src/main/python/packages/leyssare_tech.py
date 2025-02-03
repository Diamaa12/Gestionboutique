import datetime
import json
#from distutils.command.install import value
from functools import partial
from itertools import zip_longest
from operator import index

from PySide6 import QtWidgets
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextDocument, QAction
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QMainWindow, QMenuBar, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QStyle)


#from gestion_boutique_console import handler
#from src.main.python.packages.api.constants import PATH_PRODUCT_NAME, PATH_NO_BOYED_PRODUCT, PATH_BOYED_PRODUCT, \
    #PATH_TTL_SOMME_FOR_ANY_UNITE, PATH_CELL_PRICE_PER_UNITE, PATH_BUYED_PRICE_PER_UNITE, \
    #PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM
from .api.gestion_prix_et_quantite import GestionPrixQauntite
from .api.gestion_quantite import GestionQuantite
from .api.gestion_prix import GestionPrix
from .api.gestion_boutique import DatabasePostgre, Boutiquehandler
from .api.product_manager import ProductManager
from .gestion_class_aditionnel import DialogConfirmation
from .gestion_menu_bar import AddProduitBarDialog, DeleteProduitBarDialog, \
    HistoriqueProduitBarDialog, ShowHistoriqueQuantiteForProduct


def db_connector():
    host = "localhost"
    port = 5432
    user = 'postgres'
    password = 'Galle11'
    database = 'gestion_stock'
    return [host, port, user, password, database]

class LeyssareTech(QMainWindow):

    def __init__(self, ctx):
        super().__init__()
        self.setWindowTitle("Leyssare Tech")
        self.ctx = ctx
        self.setGeometry(100, 100, 700, 900)

        # Dictionnaire pour suivre les widgets associés à chaque produit
        self.product_widgets = {}

        self.produits_names = []
        self.edit_quantite_kg_unite = []
        self.edit_quantite_vendu = []
        self.edit_quantite_restants = []
        self.edit_prix_d_achat = []
        self.edit_prix_de_vente = []
        self.edit_total_vendu = []
        self.edit_total_non_vendu = []

        self.api_recup_quantite = GestionQuantite()
        self.api_gestion_prix = GestionPrix()
        self.api_gestion_prix_quantite = GestionPrixQauntite()
        self.api_db_postgre = DatabasePostgre()
        connexion = self.api_db_postgre.connect_to_db(*db_connector())
        self.api_boutique = Boutiquehandler(connexion)

        #self.items_restant = self.api_recup_quantite.retourne_quantite_restant()
        #print(self.items_restant)
        self.send_signal = []
        self.leytech_ui()

    def leytech_ui(self):
        self.my_main_window()
        self.create_widget()
        self.create_layout()
        self.create_qwidgets_conteneur()
        self.add_layout_to_layout()
        self.add_layouts_to_widgets()
        self.set_layouts_to_widgets()
        self.add_widgets_to_layouts()
        #methodes de gestions de menubar
        self.gestion_menu_bar1()
        self.gestion_menu_bar2()
        #self.setplaceholder_as_defaut()
        self.set_default_placeholders()
        self.ttl_sommes_vendu_de_tous_les_produit()
        self.set_placeholder_ttl_somme_vendu_pour_chaque_produit()
        self.set_placeholder_ttl_somme_non_vendu_pour_chaque_produit()
        self.set_placeholder_quantite_restante_pour_chaque_produit()
        self.setup_connections()
        #self.show_quantite_restante()
        #self.setup_connexions_for_gestion_prix()
        #self.update_product_input_state()
        self.modify_widget()
    def format_monnaie(self, valeur):
        """
        Formate un nombre pour l'afficher comme une monnaie :
        - Ajoute des espaces comme séparateur de milliers
        - Supprime les zéros inutiles après la virgule

        Exemple : 1000.00 -> 1 000
                  12345.67 -> 12 345.67
                  12345.00 -> 12 345
        """
        # Utiliser format pour ajouter un séparateur d'espace
        if valeur:
            valeur_formatee = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
            # Supprimer ',00' si les centimes sont 0
            if valeur_formatee.endswith(",00"):
                valeur_formatee = valeur_formatee[:-3]
            return valeur_formatee
    #Les fonctions placeholders permettent d'afficher les valeurs correspondante pour chaque QlineEdit et Qlabel
    def set_default_placeholders(self):
        for index, product_name in enumerate(self.product_names):
            data = self.api_boutique.show_produit_values(product_name)
            if data:
                print(product_name, index)
                self.edit_quantite_kg_unite[index].setPlaceholderText(f"{data[0]}")
                self.edit_prix_d_achat[index].setPlaceholderText(f"{self.format_monnaie(data[1])}")
                self.edit_prix_de_vente[index].setPlaceholderText(f"{self.format_monnaie(data[2])}")

    def set_placeholder_ttl_somme_vendu_pour_chaque_produit(self):
        # Trouver l'index correspondant au produit_name
        for produit_name in self.product_names:
            id_produit = self.api_boutique.get_product_id(produit_name)
            ttl_somme_vendu_pour_chaque_produit = self.api_boutique.show_ttl_somme_vendu_pour_chaque_produit(id_produit)
            index = next((i for i, label in enumerate(self.produits_names)
                          if label.text() == produit_name), None)
            if index is not None:
                # Mettre à jour le QLabel correspondant
                self.edit_total_vendu[index].setText(f"{self.format_monnaie(ttl_somme_vendu_pour_chaque_produit)}")
            else:
                print(f"{produit_name} ne correspond pas à un produit dans l'interface.")
    def set_placeholder_ttl_somme_non_vendu_pour_chaque_produit(self):
        # Trouver l'index correspondant au produit_name
        for produit_name in self.product_names:
            id_produit = self.api_boutique.get_product_id(produit_name)
            ttl_somme_non_vendu_pour_chaque_produit = self.api_boutique.show_ttl_somme_non_vendu_pour_chaque_produit(id_produit)
            index = next((i for i, label in enumerate(self.produits_names)
                          if label.text() == produit_name), None)
            if index is not None:
                # Mettre à jour le QLabel correspondant
                self.edit_total_non_vendu[index].setText(f"{self.format_monnaie(ttl_somme_non_vendu_pour_chaque_produit)}")
            else:
                print(f"{produit_name} ne correspond pas à un produit dans l'interface.")
    def set_placeholder_quantite_restante_pour_chaque_produit(self):
        # Trouver l'index correspondant au produit_name
        for produit_name in self.product_names:
            id_produit = self.api_boutique.get_product_id(produit_name)
            quantite_restante_pour_chaque_produit = self.api_boutique.show_quantite_restante(id_produit)
            index = next((i for i, label in enumerate(self.produits_names)
                          if label.text() == produit_name), None)
            if index is not None:
                # Mettre à jour le QLabel correspondant
                self.edit_quantite_restants[index].setText(f"{quantite_restante_pour_chaque_produit}")
            else:
                print(f"{produit_name} ne correspond pas à un produit dans l'interface.")
    def create_widget(self):
        #self.product_names = ['Poulets', 'Dindes', 'Dos', 'Pattes', 'Poussin', 'Dos']
        #On charge les noms de produits se trouvant dans le fichier json
        self.api_gestion_nom_produits = ProductManager()
        self.product_names = self.api_gestion_nom_produits.load_products()
        #On supprime les valeus vide dans cette liste
        self.product_names = [nom_produits for nom_produits in self.product_names if nom_produits]

        current_date  = datetime.date.today().strftime('%d/%m/%Y')
        self.grand_ttl = QLabel()
        self.date = QLabel(f'Date: {current_date}')
        self.btn_reset = QPushButton('Reset')
        self.btn_scannen = QPushButton('Imprimer')
        self.btn_data_download = QPushButton('Télécharger un copie')

        self.product = QLabel('Produits:')

        self.quantite_kg_unite = QLabel('Quantité/Kg/Unite:')
        self.quantite_vendu = QLabel('Quantité à vendre:')
        self.quantite_restants = QLabel('Quantité Restants:')
        self.prix_d_achat = QLabel('Prix D\'achat/kg/unite:')
        self.prix_de_vente = QLabel('Prix de Vente:')
        self.total_vendu = QLabel('Total Vendu:')
        self.total_non_vendu = QLabel('Total non Vendu:')

        for item in self.product_names:

            label = QLabel(item)
            label.setProperty('class', 'product_name')
            self.produits_names.append(label)
            self.edit_quantite_kg_unite.append(QLineEdit())
            self.edit_quantite_vendu.append(QLineEdit())
            self.edit_quantite_restants.append(QLabel())
            self.edit_prix_d_achat.append(QLineEdit())
            self.edit_prix_de_vente.append(QLineEdit())
            self.edit_total_vendu.append(QLabel())
            self.edit_total_non_vendu.append(QLabel())
    def gestion_menu_bar1(self):
        # Création d'un menubar
        self.menu_files = self.menuBar()
        #Creation du menu
        menu = self.menu_files.addMenu('Menu')
        #Ajout de contenu au menu
        ajouter_produit = QAction('Ajouter un produit', self)
        supprimer_produit = QAction('Supprimer un produit', self)
        quitter = QAction('Quitter', self)
        #Ajout d'une action de type trigger pour appeler les methods suivantes
        ajouter_produit.triggered.connect(self.add_produit)
        supprimer_produit.triggered.connect(self.delete_produit)
        quitter.triggered.connect(self.close)
        #Ajouter de sous menu au Menu
        menu.addAction(ajouter_produit)
        menu.addAction(supprimer_produit)
        menu.addAction(quitter)
    def gestion_menu_bar2(self):
        menu = self.menu_files.addMenu('Historique')
        calculer_le_interval_de_vente_pour_un_produit = QAction('Historique vente pour un produit', self)
        historiqe_quantite_pour_un_produit = QAction("Historique quantite pour un produit", self)

        calculer_le_interval_de_vente_pour_un_produit.triggered.connect(self.periode_de_vente_pour_un_produit)
        historiqe_quantite_pour_un_produit.triggered.connect(self.historique_vente_pour_un_produit)

        menu.addAction(calculer_le_interval_de_vente_pour_un_produit)
        menu.addAction(historiqe_quantite_pour_un_produit)
    def my_main_window(self):
        self.main_window = QWidget()
        self.setCentralWidget(self.main_window)
    def create_layout(self):
        self.main_layout = QGridLayout()
        self.left_layout = QGridLayout()
        self.right_layout = QVBoxLayout()

        self.prices_layout = QVBoxLayout()
        self.input_items = QHBoxLayout()

    def create_qwidgets_conteneur(self):
        self.conteneur_right_layout = QWidget()
        self.conteneur_left_layout = QWidget()
    def add_layout_to_layout(self):
        #self.left_layout.addLayout(self.prices_layout, 1, 0)
        #self.left_layout.addLayout(self.input_items, 1, 1)
        pass
    def add_layouts_to_widgets(self):
        self.main_layout.addWidget(self.conteneur_left_layout, 0, 0)
        self.main_layout.addWidget(self.conteneur_right_layout, 0, 1)
    def set_layouts_to_widgets(self):
        self.main_window.setLayout(self.main_layout)
        self.conteneur_left_layout.setLayout(self.left_layout)
        self.conteneur_right_layout.setLayout(self.right_layout)

    def add_widgets_to_layouts(self):
        # Définir une taille fixe pour tous les QLineEdit
        quantite_fixed_width = 100
        quantite_fixed_height = 40
        price_fixed_width = 175
        price_fixed_height = 40

        self.left_layout.addWidget(self.product, 0, 0)

        self.left_layout.addWidget(self.quantite_kg_unite, 1, 0)
        self.left_layout.addWidget(self.prix_d_achat, 2, 0)
        self.left_layout.addWidget(self.prix_de_vente, 3, 0)
        self.left_layout.addWidget(self.quantite_vendu, 4, 0)
        self.left_layout.addWidget(self.quantite_restants, 5, 0)
        self.left_layout.addWidget(self.total_vendu, 6, 0)
        self.left_layout.addWidget(self.total_non_vendu, 7, 0)
        #Initialisation du layout  à un

        for idx, label in enumerate(self.produits_names, start=1):
            self.left_layout.addWidget(label, 0, idx)
            label.setStyleSheet('margin:10px; padding:5px;')
        for index, edit in enumerate(self.edit_quantite_kg_unite, start=1):
            edit.setFixedSize(quantite_fixed_width, quantite_fixed_height)
            self.left_layout.addWidget(edit, 1, index)
            edit.setProperty('class', 'edit_quantite_kg_unite')
        for index, edit in enumerate(self.edit_prix_d_achat, start=1):
            edit.setFixedSize(price_fixed_width, price_fixed_height)
            edit.setProperty('class', 'edit_prix_d_achat')
            self.left_layout.addWidget(edit, 2, index)
        for index, edit in enumerate(self.edit_prix_de_vente, start=1):
            edit.setFixedSize(price_fixed_width, price_fixed_height)
            edit.setProperty('class', 'edit_prix_de_vente')
            self.left_layout.addWidget(edit, 3, index)

        for index, edit in enumerate(self.edit_quantite_vendu, start=1):
            edit.setFixedSize(quantite_fixed_width, quantite_fixed_height)
            edit.setProperty('class', 'edit_quantite_vendu')
            self.left_layout.addWidget(edit, 4, index)
        for index, edit in enumerate(self.edit_quantite_restants, start=1):
            edit.setProperty('class', 'restants')
            self.left_layout.addWidget(edit, 5, index)

        for index, edit in enumerate(self.edit_total_vendu, start=1):
            edit.setProperty('class', 'total_vendue')
            self.left_layout.addWidget(edit, 6, index)
        for index, edit in enumerate(self.edit_total_non_vendu, start=1):
            edit.setProperty('class', 'total_non_vendue')
            self.left_layout.addWidget(edit, 7, index)


        #Gestion de QVboxlayout de droite
        self.right_layout.addWidget(self.date, alignment=Qt.AlignmentFlag.AlignTop)
        #On recupere la somme total dans l'api gestion_prix_quantite.somme_ttl_produit_vedue() et le passe au Qlabel
        #ttl_somme_produits_vendue = self.api_gestion_prix_quantite.somme_ttl_produits_vendue()
        self.right_layout.addWidget(self.grand_ttl)
        self.right_layout.addWidget(self.btn_data_download)
        self.right_layout.addWidget(self.btn_reset)
        self.right_layout.addWidget(self.btn_scannen)
    def setup_connections(self):

        for index in range(len(self.product_names)):
            self.edit_quantite_kg_unite[index].editingFinished.connect(
                lambda idx=index: self.on_data_edited(idx)
            )
            self.edit_prix_d_achat[index].editingFinished.connect(
                lambda idx=index: self.on_data_edited(idx)
            )
            self.edit_prix_de_vente[index].editingFinished.connect(
                lambda idx=index: self.on_data_edited(idx)
            )
        for index in range(len(self.product_names)):
            self.edit_quantite_vendu[index].editingFinished.connect(
                lambda idx=index: self.vendre_produit(idx)
            )
        #Afficher les quantite_restante
        # Connexion du signal produit_mis_a_jour au QLabel
        #Signal déclencher pour afficher le quantité restante pour chaque produit.
        self.api_boutique.qt_signal_quantite_restante.connect(self.show_quantite_restante)
        #signal déclencheur pour afficher la somme ttl vendu pour chaque produit
        self.api_boutique.qt_signal_ttl_somme_vendu_pour_chaque_produit.connect(self.show_ttl_somme_vendu_pour_chaque_produit)
        # signal déclencheur pour afficher la somme ttl vendu pour chaque produit
        self.api_boutique.qt_signal_ttl_somme_non_vendu_pour_chaque_produit.connect(self.show_ttl_somme_non_vendu_pour_chaque_produit)
        #Signal declencher pour calculer la sommes vendue de tous les produits
        self.api_boutique.qt_signal_total_somme_vendues_de_tous_les_produit.connect(self.ttl_sommes_vendu_de_tous_les_produit)
    def ttl_sommes_vendu_de_tous_les_produit(self):
        #On recupère la sommes de tous les ventes et on les affiches sur le Qlabel grand_ttl
        #A chaque fois qu'un produit est vendu, le signal defini dans api_boutique permet de mettre à jour automatiquement les donnés
        ttl_sommes_vendu_de_tous_les_produits = self.api_boutique.show_ttl_sommes_vendu_de_tous_les_produit()
        self.grand_ttl.setText(f"Total de ventes : {self.format_monnaie(ttl_sommes_vendu_de_tous_les_produits)}")
    def show_quantite_restante(self, produit_name, quantite_restante):
        """
          Met à jour le QLabel de quantité restante après la mise à jour des données.
          """
        print(f"Produit {produit_name} mis à jour : Nouvelle quantité = {quantite_restante}")

        # Trouver l'index correspondant au produit_name
        index = next((i for i, label in enumerate(self.produits_names)
                      if label.text() == produit_name), None)
        if index is not None:
            # Mettre à jour le QLabel correspondant
            self.edit_quantite_restants[index].setText(f"{quantite_restante}")
        else:
            print(f"{produit_name} ne correspond pas à un produit dans l'interface.")
    def show_ttl_somme_vendu_pour_chaque_produit(self, produit_name, ttl_somme_vendu_pour_chaque_produit):
        print(f"TTl somme vendu pour '{produit_name}' est de : {ttl_somme_vendu_pour_chaque_produit}")
        # Trouver l'index correspondant au produit_name
        index = next((i for i, label in enumerate(self.produits_names)
                      if label.text() == produit_name), None)
        if index is not None:
            # Mettre à jour le QLabel correspondant
            self.edit_total_vendu[index].setText(f"{ttl_somme_vendu_pour_chaque_produit}")
        else:
            print(f"{produit_name} ne correspond pas à un produit dans l'interface.")
    def show_ttl_somme_non_vendu_pour_chaque_produit(self, produit_name, ttl_somme_non_vendu_pour_chaque_produit):
        print(f"TTl somme non vendu pour '{produit_name}' est de : {ttl_somme_non_vendu_pour_chaque_produit}")
        # Trouver l'index correspondant au produit_name
        index = next((i for i, label in enumerate(self.produits_names)
                      if label.text() == produit_name), None)
        if index is not None:
            # Mettre à jour le QLabel correspondant
            self.edit_total_non_vendu[index].setText(f"{ttl_somme_non_vendu_pour_chaque_produit}")
        else:
            print(f"{produit_name} ne correspond pas à un produit dans l'interface.")
            self.edit_total_non_vendu[index].setText(f"0")
    def on_data_edited(self, index):
        """
        Gestion des données après l'édition d'un QLineEdit.
        """
        produit_name = self.product_names[index]
        produit_quantite = self.edit_quantite_kg_unite[index].text()
        prix_achat = self.edit_prix_d_achat[index].text()
        prix_vente = self.edit_prix_de_vente[index].text()

        validate_quantite = self.validate_item(produit_quantite)
        validate_prix_achat = self.validate_item(prix_achat)
        validate_prix_vente = self.validate_item(prix_vente)
        if validate_quantite == False:
            self.edit_quantite_kg_unite[index].setStyleSheet("border: 2px solid red;")
        if validate_prix_achat == False:
            self.edit_prix_d_achat[index].setStyleSheet("border: 2px solid red;")
        if validate_prix_vente == False:
            self.edit_prix_de_vente[index].setStyleSheet("border: 2px solid red;")
        print('L index ', index)
        print('L produit_name ', produit_name)
        print('L produit_quantite ', produit_quantite)
        print('L prix_achat ', prix_achat)
        print('L prix_vente ', prix_vente)
        #On s'assure que tous les donnés ont étés saisies.
        #Et que leur type sont du type attendu
        if  validate_quantite and validate_prix_achat and validate_prix_vente:
            # Validation des données
            if self.validate_data(produit_name, produit_quantite, prix_achat, prix_vente):
                #Appel la fenêtre de confirmation
                confirmation = DialogConfirmation(produit_name, produit_quantite, prix_achat, prix_vente, self)
                if confirmation.get_confirmation():
                    # Conversion des données et insertion dans la base de données
                    produit_quantite = int(produit_quantite)
                    prix_achat = float(prix_achat)
                    prix_vente = float(prix_vente)
                    self.api_boutique.insert_produit(produit_name, produit_quantite, prix_achat, prix_vente)
                    QMessageBox.information(self, "Succés", "Les donnés ont étés enregistré avec succés.")
                else:
                    QMessageBox.warning(self, "Annulé", "L'inscription a été annulée.")
            else:
                print("Données invalides.")
                QMessageBox.critical(self, "Erreur", "Les donnés saisies sont invalides.")
        else:
            print("Les donnés ne sont pas encore tous saisies.")
    def validate_item(self, item):
        #Cette fonction verifie si l'item inserre est de type digit
        if item:
            if item.isdigit():
                return True
            else:
                QMessageBox.critical(self, "Erreur", "Les donnés saisies sont invalides.")
                return False
        else:
            pass

    def validate_data(self, produit_name, produit_quantite, prix_achat, prix_vente):
        """
        Valide les données saisies dans les QLineEdit.
        """
        try:
            if not produit_name or not produit_name.strip():
                return False
            produit_quantite = int(produit_quantite)
            prix_achat = float(prix_achat)
            prix_vente = float(prix_vente)
            if produit_quantite <= 0 or (prix_achat <= 0 or prix_vente <= 0):
                return False
            return True
        except ValueError as e:
            print(f"L'erreur suivante est produite: {e}")
    def vendre_produit(self, index):
        produit_name = self.product_names[index]
        quantite_vendue = self.edit_quantite_vendu[index].text()
        if self.validate_celled_data(produit_name, quantite_vendue):
            #On cree un bouton de confirmation avant l'ajout de produit
            #dans la base de données
            confirmation = QMessageBox.question(self,
                                                "Confirmation de vente",
                                                f"Une vente de {quantite_vendue} Kg va être effectué pour le produit {produit_name} ?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmation == QMessageBox.StandardButton.Yes:
                self.api_boutique.insert_or_update_produit_vendu(produit_name, quantite_vendue)
            else:
                print('Vente annulé')
                QMessageBox.warning(self, "Annulé", 'La vente est annulé.')
        else:
            print('Données invalides. veillez revoir les champs.')

    def validate_celled_data(self, produit_name, quantite_vendue):
        try:
            if not produit_name or not produit_name.strip():
                print('Le nom du produit est obligatoire.')
                return False
            if not quantite_vendue.isdigit():
                print('La quantité doit être un nombre.')
                return False
            quantite_vendue = int(quantite_vendue)
            if quantite_vendue <= 0:
               print('La quantite à vendre ne peut pas être négatif. ')
               return False
            return True
        except ValueError as e:
            print(f"L'erreur suivante est produite: {e}")
    '''
    def setup_connexions_for_gestion_prix(self):
        for index in range(len(self.edit_prix_d_achat)):
            self.edit_prix_d_achat[index].editingFinished.connect(
                lambda idx=self.product_names[index], item=self.edit_prix_d_achat[index]: (
                    self.api_gestion_prix.set_buyed_price_for_one_item(idx, item.text()),
                    self.update_somme_produits_restants(idx)
                )
            )
        for index in range(len(self.edit_prix_de_vente)):
            self.edit_prix_de_vente[index].editingFinished.connect(
                lambda idx=self.product_names[index],
                       item=self.edit_prix_de_vente[index]: (self.api_gestion_prix.set_celled_price_for_one_item(idx, item.text()),
                       self.update_somme_produits_vendu(idx)
                )
            )
        self.btn_data_download.clicked.connect(self.data_download)
        self.btn_scannen.clicked.connect(self.handlerPrint)
        self.btn_reset.clicked.connect(self.reset_all_data)
    def setup_connections(self):
       #for index in range(len(self.edit_quantite_vendu)):
       #    self.edit_quantite_vendu[index].editingFinished.connect(
       #        lambda idx=self.product_names[index], item=self.edit_quantite_vendu[index]: self.api_recup_quantite.increment_quantite_vendu(idx, item.text()))


        for index in range(len(self.edit_quantite_kg_unite)):
            self.edit_quantite_kg_unite[index].editingFinished.connect(
                lambda idx=self.product_names[index],
                       item=self.edit_quantite_kg_unite[index]: self.api_recup_quantite.add_new_quantite_kg_unite(idx,
                                                                                                    item.text()))
        self.edit_quantite_vendu[0].editingFinished.connect(
            lambda idx=self.product_names[0],
                   item=self.edit_quantite_vendu[0]: self.api_recup_quantite.increment_quantite_vendu(idx,
                                                                                                      item.text()))
        self.edit_quantite_vendu[1].editingFinished.connect(
            lambda idx=self.product_names[1],
                   item=self.edit_quantite_vendu[1]: self.api_recup_quantite.increment_quantite_vendu(idx,
                                                                                                      item.text()))
        self.edit_quantite_vendu[2].editingFinished.connect(
            lambda idx=self.product_names[2],
                   item=self.edit_quantite_vendu[2]: self.api_recup_quantite.increment_quantite_vendu(idx,
                                                                                                      item.text()))
        self.edit_quantite_vendu[3].editingFinished.connect(
            lambda idx=self.product_names[3],
                   item=self.edit_quantite_vendu[3]: self.api_recup_quantite.increment_quantite_vendu(idx,
                                                                                                      item.text()))
        self.edit_quantite_vendu[4].editingFinished.connect(
            lambda idx=self.product_names[4],
                   item=self.edit_quantite_vendu[4]: self.api_recup_quantite.increment_quantite_vendu(idx,
                                                                                                      item.text()))


        for item in range(len(self.produits_names)):
            self.edit_quantite_vendu[item].editingFinished.connect(lambda name=self.product_names[item]: self.update_product_restants(name))

        self.on_editing_finish()
       #for item in range(len(self.edit_quantite_vendu)):
       #    self.edit_quantite_vendu[self.product_names[item]].textEdited.connect(lambda name=self.product_names[item]: self.update_product_input_state(name))
        """À chaque fois qu'on ajoute une quantité pour un produit, la methode on_editing_finsh()
        est appelé, pour rendre le Qlineedit modifiable."""
    def on_editing_finish(self):
        for index in range(len(self.edit_quantite_vendu)):
            self.edit_quantite_kg_unite[index].editingFinished.connect(
                lambda idx=self.edit_quantite_vendu[index]: self.update_change_line_edit(idx))
    def update_product_restants(self, product_name):
        """Méthode appelée lorsque l'utilisateur termine d'éditer le QLineEdit."""
        query = self.api_recup_quantite.print_produit_restant(product_name)
        print(query, ' et produit: ', product_name)

        # Cherche l'index associé à product_name
        index = next((i for i, lbl in enumerate(self.produits_names) if lbl.text() == product_name), None)
        print(type(index), index)
        if index is not None:
            if query >= 0:
                self.edit_quantite_restants[index].setText(f"{query}")
            else:
                self.edit_quantite_restants[index].setText("Value faux.")
        else:
            print(f"Produit {product_name} non trouvé dans produits_names.")

    def update_product_restants_save(self, index):
        """Méthode appelée lorsque l'utilisateur termine d'éditer le QLineEdit."""
        query = self.api_recup_quantite.print_produit_restant(index)
        print(query, ' et index: ', index, '')
        if query:
            self.edit_quantite_restants[index].setText(f"{query}")
        else:
            self.edit_quantite_restants[index].setText("Value faux.")
    #Mettre à jour les Qlineedit qui etaient grisé en de nouveau éditable
    def update_change_line_edit(self, le_index):
        le_index.setEnabled(True)
        le_index.setPlaceholderText('')
        le_index.setProperty('class', 'finis')
        le_index.setStyleSheet('border:none;')
    #Fonction qui transfore une schaine de caratére True en un boolean
    def str_to_bool(self, value):
        return value == True
    # Fonction pour desactiver les inputs dont la quantité est fini d'être vendu
    def update_product_input_state(self):
        #On recupére les produits marqué comme fini
        produit_epuise_dict = self.api_recup_quantite.qline_edit_desabler()
        print(type(produit_epuise_dict), produit_epuise_dict)
        #On recupère la list des QlineEdit
        line_edit_list = [item for item in self.edit_quantite_vendu]
        #On recupére une liste contenant l'index, le nom, et la valeur du produits marqué comme fini
        item_finish_list = [(index, (keys, value)) for index, (keys, value) in enumerate(produit_epuise_dict.items()) if self.str_to_bool(value)]
        print(item_finish_list)
        if item_finish_list:
            #On recupére le contenu du list crée en haut
           for index, (keys, value) in item_finish_list:
               print(index, keys, value)
               #On desactive les champs correspondant du QlineEdit
               if value:
                   line_edit_list[index].setPlaceholderText('Finish')
                   line_edit_list[index].setProperty('class', 'epuise')
                   line_edit_list[index].setEnabled(False)
               else:
                   line_edit_list[index].setEnabled(True)
    """__________________Gestion de sommes de produits_______________"""

    def update_somme_produits_vendu(self, product_name):
        """Méthode appelée lorsque l'utilisateur termine d'éditer le QLineEdit."""
        self.api_gestion_prix_quantite.data_product_manager()
        query = self.api_gestion_prix_quantite.recup_somme_vendu(produit_name=product_name)
        print(query, ' et produit: ', product_name)

        # Cherche l'index associé à product_name
        index = next((i for i, lbl in enumerate(self.produits_names) if lbl.text() == product_name), None)
        print(type(index), index)
        if index is not None:
            if query:
                print(query, ' est la somme ttl vendu')
                self.edit_total_vendu[index].setText(f"{query}")
            else:
                self.edit_total_vendu[index].setText("Value faux.")
        else:
            print(f"Produit {product_name} non trouvé dans produits_names.")
    def update_somme_produits_restants(self, product_name):
        """Méthode appelée lorsque l'utilisateur termine d'éditer le QLineEdit."""
        self.api_gestion_prix_quantite.data_product_manager()
        query = self.api_gestion_prix_quantite.recup_somme_restant(produit_name=product_name)
        print(query, ' et produit: ', product_name)

        # Cherche l'index associé à product_name
        index = next((i for i, lbl in enumerate(self.produits_names) if lbl.text() == product_name), None)
        print(type(index), index)
        if index is not None:
            if query:
                print(query, ' est la somme restante.')
                self.edit_total_non_vendu[index].setText(f"{query}")
            else:
                self.edit_total_non_vendu[index].setText("Value faux.")
        else:
            print(f"Produit {product_name} non trouvé dans produits_names.")
    def handlerPrint(self, printer):
        # Assurez-vous que 'printer' est bien une instance de QPrinter
        if not isinstance(printer, QPrinter):
            printer = QPrinter()
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
            data = PATH_BOYED_PRODUCT
            with open(data, 'r', ) as fil:
                data = json.load(fil)
            document = QTextDocument(f"{data}")
            print(data)
            document.print_(printer)
    """La méthode reset_all_data() permet de reinitialiser tous les données de tous les fichies json
    contenant les donnés renseigner par l'utilisateur.'"""
    def reset_all_data(self):
        files = [PATH_PRODUCT_NAME, PATH_BOYED_PRODUCT, PATH_NO_BOYED_PRODUCT, PATH_BUYED_PRICE_PER_UNITE, PATH_CELL_PRICE_PER_UNITE,
                 PATH_TTL_SOMME_FOR_ANY_UNITE, PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM]
        for file in files:
            try:
                with open(file, 'r+', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    for key in data.keys():
                        data[key] = 0
                    print(data)
                    json_file.seek(0)
                    json.dump(data, json_file, indent=4)
                    json_file.truncate()
                print(f"{file} a été reinitialise avec succés.")
            except FileNotFoundError as e:
                print("{file} n\'existe pas. ")
    def data_download(self):
        print('Données Téléchargé')'''

    def modify_widget(self):
        self.conteneur_right_layout.setObjectName("conteneur_right_layout")
        self.conteneur_left_layout.setObjectName("conteneur_left_layout")
        self.main_window.setObjectName("main_layout")

        #cibler les Label par un setProperty qui equivaut à une class html
        self.date.setProperty('class', 'date')
        self.product.setProperty('class', 'product')

        self.quantite_kg_unite.setProperty('class', 'quantite_kg_unite')
        self.quantite_vendu.setProperty('class', 'quantite_vendu')
        self.quantite_restants.setProperty('class', 'quantite_restants')
        self.prix_d_achat.setProperty('class', 'prix_d_achat')
        self.prix_de_vente.setProperty('class', 'prix_de_vente')
        self.total_vendu.setProperty('class', 'total_vendu')
        self.total_non_vendu.setProperty('class', 'total_non_vendu')

        self.right_layout.setSpacing(20)
        self.right_layout.setContentsMargins(20, 20, 20, 20)


        #self.conteneur_right_layout.setStyleSheet('background-color:#f76151;')
        #self.conteneur_left_layout.setStyleSheet('background-color:#9ac2f2;')
        #self.main_window.setStyleSheet('border:2px solid green;')
        self.left_layout.setSpacing(50)
        self.prices_layout.setContentsMargins(25, 0, 0, 15)
        self.left_layout.setContentsMargins(15, 5, 5, 25)
        ctx = self.ctx.get_resource('leyssare_tech.css')
        with open(ctx, 'r') as f:
            self.setStyleSheet(f.read())
    #Fonctions de gestions du Menubar1
    def add_produit(self):
        print('ajouter un produit')
        add_produit_dialog = AddProduitBarDialog(self)
        add_produit_dialog.produit_a_ajouter.connect(self.receive_add_produit)
        add_produit_dialog.exec()
    def delete_produit(self):
        delete_produit_dialog = DeleteProduitBarDialog(self)
        delete_produit_dialog.produit_a_supprimer.connect(self.receive_delete_produit)
        delete_produit_dialog.exec()
        print('La fonction delete produit')

    def receive_add_produit(self, produit_name):
        if produit_name.strip() and not None:
            if produit_name not in self.product_names:
                self.api_gestion_nom_produits.add_product(produit_name)
            else:
                print("Le produit se trouve dèja dans la liste des produits.")
                QMessageBox.warning(self, "Erreur", "Le produit est dèja dans la liste des produits.")
        else:
            print("Veuillez entrer un nom de produit valide.")

    def receive_delete_produit(self, produit_name):
        print(f"Le produit à supprimer est: {produit_name}")
        if produit_name in self.product_names:
            self.api_gestion_nom_produits.delete_product(produit_name)
        else:
            QMessageBox.warning(self, "Erreur", "Le produit que vous voulez supprimer n'existe pas.")
            print(f"Le produit {produit_name} n'est pas dans la liste des produits.")

    #Fonctions de gestion MenuBar2
    def periode_de_vente_pour_un_produit(self):
        print('calculer la vente pour un produit du mois au mois')
        calcul_periodique = HistoriqueProduitBarDialog(self.product_names)
        calcul_periodique.signal_calcul_periodique.connect(self.receive_periodique_de_vente_pour_un_produit)
        calcul_periodique.exec()
    def receive_periodique_de_vente_pour_un_produit(self, produit_name, date_debut, date_fin):
        if produit_name.strip() and not None:
            print(f"Le produit {produit_name} est dans la liste des produits.")
            print(f"Date de début : {date_debut.toString('dd/MM/yyyy')}")
            print(f"Date de fin : {date_fin.toString('dd/MM/yyyy')}")
            self.api_boutique.get_historique_vente_par_plage_horaire(produit_name, date_debut.toPython(), date_fin.toPython())
        else:
            print('le nom de produit entré est invalide.')
    def historique_vente_pour_un_produit(self):
        print('Le signal est émis.')
        historique_quantite = ShowHistoriqueQuantiteForProduct(self.product_names)
        historique_quantite.signal_historique_quantite.connect(self.receive_historique_quantite)
        historique_quantite.exec()
    def receive_historique_quantite(self, produit_name):
        print(f"Le produit {produit_name} est dans la liste des produits.")
        if produit_name.strip() and not None:
            self.api_boutique.show_historique_quantite_for_one_product(produit_name)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    main_window = LeyssareTech(ctx=app)
    main_window.show()
    sys.exit(app.exec())