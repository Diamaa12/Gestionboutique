import pathlib

from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QLayout, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QSizePolicy, QFormLayout

import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QMenuBar, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, \
    QTextEdit
from PySide2.examples.corelib.tools.settingseditor.settingseditor import MainWindow



class BBLTechnologie(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BBLTechnologie')
        self.setGeometry(250, 250, 800, 600)
        self.setup_ui()
    def setup_ui(self):

        self.create_widget()
        self.create_layout()
        self.create_qwidgets_conteneur()
        self.add_wigets_to_layouts()
        self.add_layout_to_layouts()
        self.set_layout_to_qwidgets()


        self.setup_connections()
        self.modify_widget()

    def create_widget_group(self, widgets):
        """Crée un QLabel à partir d'une liste de widgets"""
        layout = QHBoxLayout()
        self.container = QWidget()
        for widget in widgets:
            layout.addWidget(widget)
        self.container.setLayout(layout)
        return self.container

    def create_widget(self):
        self.list_product_name = ['Poulets', 'Dindes', 'Dos', 'Pattes']
        self.list_product_price = ['Produits:', 'Quantité vendu:', 'Quantite restant:', 'Prix d achat', 'Prix de vente', 'Prix ttl vendu']
        self.product_name_label = [QLabel(item) for item in self.list_product_name]
        self.product_price_label = [QLabel(item) for item in self.list_product_price]
        self.edit_list = []
        for item in self.list_product_price:
            self.edit_list.append([QLineEdit() for _ in range(len(self.list_product_name))])
        #self.edit_list_group = [self.create_widget_group(self.edit_list) for _ in range(len(self.list_product_name))]
        self.date = QLabel('Date:')
    def add_wigets_to_layouts(self):
        for item in self.product_name_label:
            self.nav_menu_layout.addWidget(item)
        for label, l_edit in zip(self.product_price_label, self.edit_list):
            for item in l_edit:
                self.le_content.addWidget(item)
            self.left_menu_layout.addRow(label, self.le_content)
        self.right_menu_layout.addWidget(self.date)
    def modify_widget(self):

        #self.conteneur_nav_menu.setObjectName("conteneur_nav_menu")
        self.conteneur_right_menu.setObjectName("conteneur_right_menu")
        self.conteneur_left_menu.setObjectName("conteneur_left_menu")
        self.conteneur_form_items.setObjectName("conteneur_form_items")

        self.conteneur_left_menu.setStyleSheet('background-color:#9ac2f2;')
        self.conteneur_form_items.setStyleSheet('background-color:#90f1a5;')
        self.conteneur_right_menu.setStyleSheet('background-color:#f76151;')
        self.conteneur_nav_menu.setStyleSheet('background-color:#4c4c4c;')
        self.conteneur_form_items.setStyleSheet('background-color:#b6845a; border:20x solid green;')
        fil = pathlib.Path(__file__).parent / 'resources/base/bbltech.css'

        if fil.exists():
            with open(fil, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(fil)
            print('Le fichier ne existe pas.')
    def create_layout(self):
        self.menu_bar = self.menuBar()

        # Création du layout principal en grille
        self.main_layout = QGridLayout()
        # Nav menu
        self.nav_menu_layout = QHBoxLayout()
        # Menu latéral gauche
        self.left_menu_layout = QFormLayout()
        # Menu latéral droit
        self.right_menu_layout = QVBoxLayout()
        self.le_content = QHBoxLayout()

    def create_qwidgets_conteneur(self):
        self.conteneur_nav_menu = QWidget()
        self.conteneur_right_menu = QWidget()
        self.conteneur_left_menu = QWidget()
        self.conteneur_form_items = QWidget()



    def set_layout_to_qwidgets(self):
        # Widget pricipal
        # Création du widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Add conteneur pricipal du fenêtre
        self.central_widget.setLayout(self.main_layout)
        self.conteneur_nav_menu.setLayout(self.nav_menu_layout)
        self.conteneur_right_menu.setLayout(self.right_menu_layout)
        self.conteneur_left_menu.setLayout(self.left_menu_layout)
        self.conteneur_form_items.setLayout(self.le_content)
    def add_layout_to_layouts(self):

       ## Ajouter le menu de navigation en haut de la grille
       #self.main_layout.addLayout(self.nav_menu_layout, 0, 1)
       ## Ajouter le menu latéral gauche dans la grille
       #self.main_layout.addLayout(self.left_menu_layout, 1, 1)
       ## Ajouter le contenu central dans la grille
       #self.main_layout.addLayout(self.right_menu_layout, 0, 2)
        # Ajouter le menu latéral droit dans la grille
        #self.main_layout.addLayout(self.right_menu_layout, 1, 2)
        self.main_layout.addWidget(self.conteneur_nav_menu, 0, 0)
        self.main_layout.addWidget(self.conteneur_left_menu, 1, 0)
        self.main_layout.addWidget(self.conteneur_right_menu, 0, 1)
        self.left_menu_layout.addWidget(self.conteneur_form_items)




    def setup_connections(sefl):
        pass
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = BBLTechnologie()
    main_window.show()
    sys.exit(app.exec_())