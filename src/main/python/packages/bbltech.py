#from unittest.mock import right

from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QLayout, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QSizePolicy, QApplication

import sys


class BBLTech(QMainWindow):
    def __init__(self, ctx):
        super().__init__()
        self.setWindowTitle('BBLTech')
        self.setGeometry(100, 100, 800, 600)
        self.ctx = ctx
        self.setup_ui()
    def setup_ui(self):
        self.create_widget()
        self.create_layout()
        self.add_layout_to_layouts()
        self.add_wigets_to_layouts()
        self.setup_connections()
        self.modify_widget()

    def create_widget(self):
        #Widget menu gauche
        self.label_produits = QLabel('Produits:')
        self.quantite_kg_unite = QLabel('Quantité/Kg/Unite:')
        self.quantite_vendu = QLabel('Quantité Vendu:')
        self.quantite_restants = QLabel('Quantité Restants:')
        self.prix_d_achat = QLabel('Prix D\'achat/kg/unite:')
        self.prix_de_vente = QLabel('Prix de Vente:')
        self.total_vendu = QLabel('Total Vendu:')
        self.total_non_vendu = QLabel('Total non Vendu:')
        #widget menu droite
        self.date = QLabel('Date:')
        #Widget nav en haut
        self.list_product_name = []
        items_name = ['Poulets', 'Dindes', 'Pattes', 'Dos', 'Foie']
        for item in items_name:
            item = QLabel(item)
            self.list_product_name.append(item)
        #Widget au centre
        self.edit_quantite_kg_unite = []
        self.edit_quantite_vendu = []
        self.edit_quantite_restants = []
        self.edit_prix_d_achat = []
        self.edit_prix_de_vente = []
        self.edit_total_vendu = []
        self.edit_total_non_vendu = []

        for _ in enumerate(self.list_product_name):
            self.edit_quantite_kg_unite.append(QLineEdit())
            self.edit_quantite_vendu.append(QLineEdit())
            self.edit_quantite_restants.append(QLabel('0.00'))
            self.edit_prix_d_achat.append(QLineEdit())
            self.edit_prix_de_vente.append(QLineEdit())
            self.edit_total_vendu.append(QLabel('0.00'))
            self.edit_total_non_vendu.append(QLabel('0.00'))

    def modify_widget(self):
       #size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
       #self.edit_quantite_kg_unite.setSizePolicy(size_policy)
       #self.edit_quantite_vendu.setSizePolicy(size_policy)
       #self.edit_quantite_restants.setSizePolicy(size_policy)
       #self.edit_prix_d_achat.setSizePolicy(size_policy)
       #self.edit_prix_de_vente.setSizePolicy(size_policy)
       #self.edit_total_vendu.setSizePolicy(size_policy)
       #self.edit_total_non_vendu.setSizePolicy(size_policy)

        # aplication de mise en forme depuis le fichier bbl_style.css
        ctx = self.ctx.get_resource('bbltech.css')
        #ciblage de layout en css
        self.central_widget.setObjectName("central_widget")
        self.nav_menu_layout.setObjectName("nav_menu_layout")
        self.left_menu_layout.setObjectName("left_menu_layout")
        self.center_layout.setObjectName("center_layout")
        self.right_menu_layout.setObjectName("right_menu_layout")
        #lecture du fichier css
        with open(ctx, 'r') as f:
            self.setStyleSheet(f.read())
    def create_layout(self):
        self.menu_bar = self.menuBar()
        # Création du widget central
        self.central_widget = QWidget()
        # Création du layout principal en grille
        self.main_layout = QGridLayout()
        # Nav menu
        self.nav_menu_layout = QHBoxLayout()
        # Menu latéral gauche
        self.left_menu_layout = QVBoxLayout()
        # Contenu central
        self.center_layout = QHBoxLayout()
        # Menu latéral droit
        self.right_menu_layout = QVBoxLayout()
        #
        #Les layouts conteneur d'autres layouts
        self.conteneur_widget_center_layout = QWidget()
    def add_layout_to_layouts(self):
        #Widget pricipal
        self.setCentralWidget(self.central_widget)
        #Add conteneur pricipal du fenêtre
        self.central_widget.setLayout(self.main_layout)
        # Ajouter le menu de navigation en haut de la grille
        self.main_layout.addLayout(self.nav_menu_layout, 0, 1)
        # Ajouter le menu latéral gauche dans la grille
        self.main_layout.addLayout(self.left_menu_layout, 1, 0)
        # Ajouter le contenu central dans la grille
        self.main_layout.addWidget(self.conteneur_widget_center_layout, 1, 1)
        # Ajouter le menu latéral droit dans la grille
        self.main_layout.addLayout(self.right_menu_layout, 1, 2)
        #
        #Layout conteneur d'autres Layouts
        self.conteneur_widget_center_layout .setLayout(self.center_layout)
    def add_wigets_to_layouts(self):
        self.left_menu_layout.addWidget(self.label_produits)
        self.left_menu_layout.addWidget(self.quantite_kg_unite)
        self.left_menu_layout.addWidget(self.quantite_vendu)
        self.left_menu_layout.addWidget(self.quantite_restants)
        self.left_menu_layout.addWidget(self.prix_d_achat)
        self.left_menu_layout.addWidget(self.prix_de_vente)
        self.left_menu_layout.addWidget(self.total_vendu)
        self.left_menu_layout.addWidget(self.total_non_vendu)
        #Ajouter les noms de produits
        for item in self.list_product_name:
            self.nav_menu_layout.addWidget(item)
        #Ajouter la date
        self.right_menu_layout.addWidget(self.date)
        #Ajouter les widgets du centre
        for item in self.edit_quantite_kg_unite:
            self.center_layout.addWidget(item)
        for item in self.edit_quantite_vendu:
            self.center_layout.addWidget(item)
        for item in self.edit_quantite_restants:
            self.center_layout.addWidget(item)
        for item in self.edit_prix_d_achat:
            self.center_layout.addWidget(item)
        for item in self.edit_prix_de_vente:
            self.center_layout.addWidget(item)
        for item in self.edit_total_vendu:
            self.center_layout.addWidget(item)
        for item in self.edit_total_non_vendu:
            self.center_layout.addWidget(item)
    def setup_connections(sefl):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = BBLTech(context=None)
    main_window.show()
    sys.exit(app.exec_())
