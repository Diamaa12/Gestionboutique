import json
from collections import defaultdict
from wave import Error

from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QSizePolicy, QFrame



class MyMainWindow(QMainWindow):
    def __init__(self, ctx):
        super().__init__()
        self.setWindowTitle('BBLTech')
        self.context = ctx

        self.produits_names = []
        self.edit_quantite_kg_unite = []
        self.edit_quantite_vendu = []
        self.edit_quantite_restants = []
        self.edit_prix_d_achat = []
        self.edit_prix_de_vente = []
        self.edit_total_vendu = []
        self.edit_total_non_vendu = []

        self.setup_ui()

    def setup_ui(self):
        self.create_widget()
        self.modify_widget()
        self.create_layout()
        self.add_widgets_to_layout()
        self.add_layout_to_layouts()
        self.setup_connections()

    def create_widget(self):

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.label_produits = QLabel('Produits:')
        self.quantite_kg_unite = QLabel('Quantité/Kg/Unite:')
        self.quantite_vendu = QLabel('Quantité Vendu:')
        self.quantite_restants = QLabel('Quantité Restants:')
        self.prix_d_achat = QLabel('Prix D\'achat/kg/unite:')
        self.prix_de_vente = QLabel('Prix de Vente:')
        self.total_vendu = QLabel('Total Vendu:')
        self.total_non_vendu = QLabel('Total non Vendu:')
        self.date = QLabel('Date:')

        tab_items = ["Poulets", "Dindes", "Foie", "Pattes", "Dos"]

        for item in tab_items:
            label = QLabel(item)
            self.produits_names.append(label)
            self.edit_quantite_kg_unite.append(QLineEdit())
            self.edit_quantite_vendu.append(QLineEdit())
            self.edit_quantite_restants.append(QLabel('0'))
            self.edit_prix_d_achat.append(QLineEdit())
            self.edit_prix_de_vente.append(QLineEdit())
            self.edit_total_vendu.append(QLineEdit())
            self.edit_total_non_vendu.append(QLineEdit())

    def modify_widget(self):
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.quantite_kg_unite.setSizePolicy(size_policy)
        self.quantite_vendu.setSizePolicy(size_policy)
        self.quantite_restants.setSizePolicy(size_policy)
        self.prix_d_achat.setSizePolicy(size_policy)
        self.prix_de_vente.setSizePolicy(size_policy)
        self.total_vendu.setSizePolicy(size_policy)
        self.total_non_vendu.setSizePolicy(size_policy)

        #ciblage de widgets en css
        self.label_produits.setObjectName("label_produits")
        self.quantite_kg_unite.setObjectName("quantite_kg_unite")
        self.quantite_vendu.setObjectName("quantite_vendu")
        self.quantite_restants.setObjectName("quantite_restants")
        self.prix_d_achat.setObjectName("prix_d_achat")
        self.prix_de_vente.setObjectName("prix_de_vente")
        self.total_vendu.setObjectName("total_vendu")
        self.total_non_vendu.setObjectName("total_non_vendu")

        #aplication de mise en forme depuis le fichier bbl_style.css
        ctx = self.context.get_resource('bbl_style.css')
        with open(ctx, 'r') as f:
            self.setStyleSheet(f.read())

    def create_layout(self):
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setSpacing(10)
        self.vertical_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def add_layout_to_layouts(self):
        self.main_layout.addLayout(self.grid_layout)
        #self.main_layout.addLayout(self.central_widget)

    def add_widgets_to_layout(self):

        self.grid_layout.addWidget(self.label_produits, 0, 0)
        self.grid_layout.addWidget(self.quantite_kg_unite, 1, 0)
        self.grid_layout.addWidget(self.quantite_vendu, 2, 0)
        self.grid_layout.addWidget(self.quantite_restants, 3, 0)
        self.grid_layout.addWidget(self.prix_d_achat, 4, 0)
        self.grid_layout.addWidget(self.prix_de_vente, 5, 0)
        self.grid_layout.addWidget(self.total_vendu, 6, 0)
        self.grid_layout.addWidget(self.total_non_vendu, 7, 0)

        # Ajouter chaque QLabel à la layout principale
        for index, label in enumerate(self.produits_names, start=1):
            label.setProperty('class', 'label_produits')
            self.grid_layout.addWidget(label, 0, index)
            self.grid_layout.setColumnStretch(index, 1)
        for index, edit in enumerate(self.edit_quantite_kg_unite, start=1):
            self.grid_layout.addWidget(edit, 1, index)
        for index, edit in enumerate(self.edit_quantite_vendu, start=1):
            self.grid_layout.addWidget(edit, 2, index)
        for index, edit in enumerate(self.edit_quantite_restants, start=1):
            self.grid_layout.addWidget(edit, 3, index)
        for index, edit in enumerate(self.edit_prix_d_achat, start=1):
            self.grid_layout.addWidget(edit, 4, index)
        for index, edit in enumerate(self.edit_prix_de_vente, start=1):
            self.grid_layout.addWidget(edit, 5, index)
        for index, edit in enumerate(self.edit_total_vendu, start=1):
            self.grid_layout.addWidget(edit, 6, index)
        for index, edit in enumerate(self.edit_total_non_vendu, start=1):
            self.grid_layout.addWidget(edit, 7, index)
        self.grid_layout.addWidget(self.date, 0, 8)

    def setup_connections(self):
        #for item in self.edit_quantite_kg_unite:
        #   item.editingFinished.connect(self.calcule_total_vendu)
        #for item in self.edit_quantite_vendu:
        #    item.editingFinished.connect(self.calcule_total_vendu)
        #for item in self.edit_prix_d_achat:
        #    item.editingFinished.connect(self.calculate_somme_vendu)
        #for item in self.edit_prix_de_vente:
        #    item.editingFinished.connect(self.calculate_somme_vendu)
        #Gestion de quantité recu
        #self.edit_quantite_kg_unite[0].editingFinished.connect(self.editer_nombre_poulets)
        #self.edit_quantite_kg_unite[1].editingFinished.connect(self.editer_nombre_dindes)
        #self.edit_quantite_kg_unite[2].editingFinished.connect(self.editer_nombre_foie)
        #self.edit_quantite_kg_unite[3].editingFinished.connect(self.editer_nombre_pattes)
        #self.edit_quantite_kg_unite[4].editingFinished.connect(self.editer_nombre_dos)

        for index in range(len(self.edit_quantite_kg_unite)):
            print(index)
            self.edit_quantite_kg_unite[index].editingFinished.connect(
                lambda item=self.edit_quantite_kg_unite[index], indice=index: self.nombre_produits_unite_kg(item, indice)
            )
        """#Gestion de quantité vendu
        #On boucle sur le tableau de self.edit_quantite_vendu et on connecte
        #chaque QLineEdit contenu dans la list à la methode nombre_produits_vendue"""
        for index in range(len(self.edit_quantite_vendu)):
            print(index)
            self.edit_quantite_vendu[index].editingFinished.connect(
                lambda item=self.edit_quantite_vendu[index], indice=index: self.nombre_produits_vendu(item, indice)
            )
        """Initialisation de signal qui gere la quantité restant de produits."""
        for index in range(0, 5):
            self.edit_quantite_kg_unite[index].editingFinished.connect(lambda item=self.edit_quantite_kg_unite[index], idx=index: self.nombre_produits_restants(item, idx))
            self.edit_quantite_vendu[index].editingFinished.connect(lambda item=self.edit_quantite_vendu[index], idx=index: self.nombre_produits_restants(item, idx))
            #self.edit_quantite_vendu[index].editingFinished.connect(
            #    lambda item=self.edit_quantite_restants[index], indice=index: self.nombre_produits_restants(item, indice))

        #self.edit_quantite_vendu[1].editingFinished.connect(self.editer_nombre_dindes)
        #self.edit_quantite_vendu[2].editingFinished.connect(self.editer_nombre_foie)
        #self.edit_quantite_vendu[3].editingFinished.connect(self.editer_nombre_pattes)
        #self.edit_quantite_vendu[4].editingFinished.connect(self.editer_nombre_dos)
    #Gestion de quantité vendu
    
    def gestion_quantite_untie_kg(self, item: list[QLineEdit], indice: int) -> dict:

        if item.text().strip().isdigit():
            item_nombre = int(item.text())
            if item_nombre > 250:
                print('La quantité ne doit pas depassé 250 kg / unité')
                item.setText('Veleur incorrecte!')
                item.setStyleSheet("border: 1px solid red; color:red;")
                return None
            #data_json = {
            #    "poulets": item_nombre,
            #    "dindes": item_nombre,
            #    "foie": item_nombre,
            #    "pattes": item_nombre,
            #    "dos": item_nombre,
            #}
            print(item_nombre, indice)
            try:
                produit_quantite_items = 'noms_produits.json'
                # on ajoute pour chaque item la nouvelle valeur vendue
                with open(produit_quantite_items, 'r', encoding='utf-8') as f:
                    item_names = json.load(f)
                print(item_names)
                if indice == 0:
                    item_names['poulets'] = item_nombre
                    print(f"On a recu {item_nombre} poulets.")
                elif indice == 1:
                    item_names['dindes'] = item_nombre
                    print(f"On a recu  {item_nombre} kg de dindes.")
                elif indice == 2:
                    item_names['foie'] = item_nombre
                    print(f"On a recu {item_nombre} kg de foie.")
                elif indice == 3:
                    item_names['pattes'] = item_nombre
                    print(f"On a recu {item_nombre} kg de pattes.")
                elif indice == 4:
                    item_names['dos'] = item_nombre
                    print(f"On a vendu aujoud'hui {item_nombre} dos.")
                    # on ajoute pour chaque item la nouvelle valeur vendue
                with open(produit_quantite_items, 'w', encoding='utf-8') as f:
                    json.dump(item_names, f, indent=4)
                print(item_names)
                return item_names
            except ValueError as e:
                print(f"L'erreur: {e} est survenue!")
            except IOError as e:
                print("L'erreur: ", e, " est survenue!")
            except TypeError as e:
                print("L'erreur: ", e, " est survenue!")
        else:
            print('Données entré nom valide')
            self.edit_quantite_kg_unite[1].setStyleSheet("border: 1px solid red; color:red;")
            return None

    #S'assurer que le quantité recu est conforme
    #def quantite_produit_verifier(self, item):
    #    if item.text().strip().isdigit():
    #        valeur_converteur = int(item.text())
    #        if valeur_converteur > 200:
    #            item.setText('Veleur incorrecte!')
    #            item.setStyleSheet("border: 1px solid red; color:red;")
    #            print(valeur_converteur, 'Veleur entrer incorrect! valeur maximale 200')
    #            return None
    #        else:
    #            print(type(valeur_converteur), valeur_converteur)
    #            return valeur_converteur
    #    else:
    #        print('valeur doit être un nombre entier!')
    #        return None
#
    #def editer_nombre_poulets(self):
    #    poulets = self.edit_quantite_kg_unite[0]
    #    poulets.setPlaceholderText('Nombre de poulets:')
    #    poulets.setStyleSheet('color:black;')
    #    print(poulets.text(), 'Voyons voir')
    #    if poulets.text().strip():
    #        print(poulets.text(), 'Voyons voir')
    #        le_checker = self.quantite_produit_verifier(poulets)
    #        print(le_checker)
    #        if le_checker is not None:
    #            poulets.setStyleSheet("border: 1px solid green;")
    #            print(le_checker)
    #        else:
    #            poulets.setStyleSheet("border: 1px solid red; color:red;")
    #    else:
    #        self.edit_quantite_kg_unite[0].setStyleSheet("border: 1px solid red; color:red;")
#
    #def editer_nombre_dindes(self):
    #    dindes = self.edit_quantite_kg_unite[1]
    #    if dindes.text().strip():
    #        le_checker = self.quantite_produit_verifier(dindes)
    #        if le_checker is not None:
    #            dindes.setStyleSheet("border: 1px solid green;")
    #            print(le_checker)
    #        else:
    #            print('donnés invalides.')
    #    else:
    #        self.edit_quantite_kg_unite[1].setStyleSheet("border: 1px solid red; color:red;")
#
    #def editer_nombre_foie(self):
    #    foie = self.edit_quantite_kg_unite[2]
    #    if foie.text().strip():
    #        le_checker = self.quantite_produit_verifier(foie)
    #        if le_checker is not None:
    #            foie.setStyleSheet("border: 1px solid green;")
    #            print(le_checker)
    #        else:
    #            print('donnés invalides.')
    #    else:
    #        self.edit_quantite_kg_unite[2].setStyleSheet("border: 1px solid red; color:red;")
#
    #def editer_nombre_pattes(self):
    #    pattes = self.edit_quantite_kg_unite[3]
    #    if pattes.text().strip():
    #        le_checker = self.quantite_produit_verifier(pattes)
    #        if le_checker is not None:
    #            pattes.setStyleSheet("border: 1px solid green;")
    #            print(le_checker)
    #        else:
    #            print('donnés invalides.')
    #    else:
    #        self.edit_quantite_kg_unite[3].setStyleSheet("border: 1px solid red; color:red;")
#
    #def editer_nombre_dos(self):
    #    dos = self.edit_quantite_kg_unite[4]
    #    if dos.text().strip():
    #        le_checker = self.quantite_produit_verifier(dos)
    #        if le_checker is not None:
    #            dos.setStyleSheet("border: 1px solid green;")
    #            print(le_checker)
    #        else:
    #            print('donnés invalides.')
    #    else:
    #        self.edit_quantite_kg_unite[4].setStyleSheet("border: 1px solid red; color:red;")
#
    #Gestion de quantité vendu
    def gestion_de_quantite_vendu(self, item: list[QLineEdit], indice: int) -> dict:
        if item.text().strip().isdigit():
            q_vendu = int(item.text())
            #On recupère notre fichier json
            data_base_json = "quantite_vendu.json"
            try:
                #On ouvre le fichier quantite_produits.json
                produit_quantite_items = 'noms_produits.json'
                # on ajoute pour chaque item la nouvelle valeur vendue
                with open(produit_quantite_items, 'r', encoding='utf-8') as f:
                    item_names = json.load(f)


                #On ouvre lit le contenu du fichier quantite_vendu.json
                with open(data_base_json, 'r', encoding='utf-8') as f:
                    ajout_quantite_vendu = json.load(f)
                #on ajoute pour chaque item la nouvelle valeur vendue
                if indice == 0:
                    ajout_quantite_vendu['poulets'] += q_vendu

                    print(f"On a vendu aujoud'hui {q_vendu} poulets.")
                elif indice == 1:
                    ajout_quantite_vendu['dindes'] += q_vendu
                    print(f"On a vendu aujoud'hui {q_vendu} dindes.")
                elif indice == 2:
                    ajout_quantite_vendu['foie'] += q_vendu
                    print(f"On a vendu aujoud'hui {q_vendu} foie.")
                elif indice == 3:
                    ajout_quantite_vendu['pattes'] += q_vendu
                    print(f"On a vendu aujoud'hui {q_vendu} pattes.")
                elif indice == 4:
                    ajout_quantite_vendu['dos'] += q_vendu
                    print(f"On a vendu aujoud'hui {q_vendu} dos.")
                with open(data_base_json, 'w', encoding='utf-8') as f:
                    json.dump(ajout_quantite_vendu, f, indent=4)
                return ajout_quantite_vendu
            except ValueError as e:
                print(f"L'erreur: {e} est survenue!")
            except IOError as e:
                print("L'erreur: ", e, " est survenue!")
            except TypeError as e:
                print("L'erreur: ", e, " est survenue!")
        else:
            print('Les donnés entrées est incorrect!')
            self.edit_quantite_vendu[indice].setStyleSheet("border: 1px solid red; color:red;")
            return None
    def gestion_quantite_restants(self) :
        # Créer un dictionnaire pour stocker les valeurs
        # Initialisation de liste pour stocker les résultats
        resultat = []
        produit_dispo_list = []
        quantite_vendu_list = []

        #recuperation de quantite produit disponible
        with open('noms_produits.json', 'r', encoding='utf-8') as f:
            noms_produits = json.load(f)
        for key, value in noms_produits.items():
            produit_dispo_list.append(value)

        #Recuperation de quantite produits vendue
        with open('quantite_vendu.json', 'r', encoding='utf-8') as f:
            quantite_vendu = json.load(f)
        for key, value in quantite_vendu.items():
            quantite_vendu_list.append(value)
        print(produit_dispo_list, quantite_vendu_list)

        # Itérer sur les deux listes en même temps et additionner les éléments d'index correspondants
        for item_dispo, item_vendu in zip(produit_dispo_list, quantite_vendu_list):
            resultat.append(item_dispo - item_vendu)
        with open('quantite_restante.json', 'w', encoding='utf-8') as f:
            json.dump(resultat, f, indent=4)
        with open('quantite_restante.json', 'r', encoding='utf-8') as f:
            quantite_restant = json.load(f)

        return quantite_restant
    #Cette fonction attend une list de Qlinedit, et l'index de chacune des QLineEdit
    def nombre_produits_unite_kg(self, item: QLineEdit, indice: int):
        product_name = item
        print(product_name, indice)
        if product_name.text().strip():
            le_checker = self.gestion_quantite_untie_kg(product_name, indice)
            if le_checker is not None:
                product_name.setStyleSheet("border: 1px solid green;")
                print(le_checker)
            else:
                print('donnés invalides.')
        else:
            self.edit_quantite_vendu[indice].setStyleSheet("border: 1px solid red; color:red;")
    def nombre_produits_vendu(self, item: list[QLineEdit], indice: int):
        product_name = item
        if product_name.text().strip():
            le_checker = self.gestion_de_quantite_vendu(product_name, indice)
            if le_checker is not None:
                product_name.setStyleSheet("border: 1px solid green;")
                print(le_checker)
            else:
                print('donnés invalides.')
        else:
            self.edit_quantite_vendu[indice].setStyleSheet("border: 1px solid red; color:red;")
    def nombre_produits_restants(self,item,  index):
        #item_restant = item

        #print(self.gestion_quantite_restants(item_restant))
        #quantite_restant = self.gestion_quantite_restants(index)
       # if quantite_restant is not None:
       #    self.edit_quantite_restants[index].setStyleSheet("border: 1px solid green;")
       # else:
       #     self.edit_quantite_restants[index].setStyleSheet("border: 1px solid red; color:red;")

        """Méthode qui récupère les valeurs des QLineEdit et met à jour le QLabel avec la somme."""
        try:
            # Récupérer la valeur des champs produits1 et produits2, en gérant les champs vides
            quantite_dispo = float(self.edit_quantite_kg_unite[index].text()) if self.edit_quantite_kg_unite[index].text() else 0
            quantite_vendu = float(self.edit_quantite_vendu[index].text()) if self.edit_quantite_vendu[index].text() else 0
            # Calculer la somme
            somme = quantite_dispo - quantite_vendu
            rst_quantite = self.gestion_quantite_restants()
            print(rst_quantite)
            if quantite_dispo and quantite_vendu != 0:
                if index == 0:
                    self.edit_quantite_restants[index].setText(str(rst_quantite[0]))
                    self.edit_quantite_restants[index].setStyleSheet("border: 1px solid green;")
                elif index == 1:
                    self.edit_quantite_restants[index].setText(str(rst_quantite[1]))
                elif index == 2:
                    self.edit_quantite_restants[index].setText(str(rst_quantite[2]))
                elif index == 3:
                    self.edit_quantite_restants[index].setText(str(rst_quantite[3]))
                elif index == 4:
                    self.edit_quantite_restants[index].setText(str(rst_quantite[4]))
                else:
                    print('erreur, index depassé')
                print("tour ", index)
                #Mettre à jour le QLabel correspondant avec le résultat

                #self.edit_quantite_restants[index].setText(str(somme))
        except ValueError:
            # En cas de saisie non numérique, afficher 0 par défaut
            self.edit_quantite_restants[index].setText("0")
            self.edit_quantite_restants[index].setStyleSheet("border: 1px solid red; color:red;")
    """       
    def recup_edit_quantite_kg_unite(self):
        poulets = self.edit_quantite_kg_unite[0]
        dindes = self.edit_quantite_kg_unite[1]
        foie = self.edit_quantite_kg_unite[2]
        pattes = self.edit_quantite_kg_unite[3]
        dos = self.edit_quantite_kg_unite[4]
        items_list = [poulets, dindes, foie, pattes, dos]
        items_is_valid = all(items.text().isdigit() for items in items_list)
        print(items_is_valid)
        if items_is_valid:
            for items in items_list:
                items.setStyleSheet("border: 1px solid green;")
                items_convert = int(items.text())
                if items_convert > 200 or items_convert is None:
                    items.setText('Veleur incorrecte!')
                    items.setStyleSheet("color:red; border: 1px solid red;")
                    print(items_convert, 'Veleur incorrecte!')
                    return None
                else:
                    print(type(items_convert), items_convert)
                    return items_convert

        else:
            poulets.setText('Valeur incorrect!')
            poulets.setStyleSheet("border: 1px solid red; color:red;")
            return None

    def recup_quantite_vendu(self):
        poulets = self.edit_quantite_vendu[0]

        if poulets.text().isdigit() and poulets.text() != '':
            poulets.setStyleSheet("border: 1px solid green;")
            valeur = int(poulets.text())
            if valeur > 300:
                poulets.setText('Veleur incorrecte!')
                poulets.setStyleSheet("color:red; border: 1px solid red;")
                print(valeur, 'Valeur incorrecte! vous ne pouvez vendre plus que ce que vous avez!')
                return None
            else:
                print(type(valeur), valeur)
                return valeur
        else:
            poulets.setText('Valeur incorrect!')
            poulets.setStyleSheet("border: 1px solid red; color:red;")
            return None

    def calcule_total_vendu(self):
        value = self.recup_edit_quantite_kg_unite()
        value2 = self.recup_quantite_vendu()
        if value is not None and value2 is not None:
            resultat = value - value2
            self.edit_quantite_restants[0].setText(str(resultat))
            self.edit_quantite_restants[0].setStyleSheet("border: 1px solid green;")
            print(resultat)

    def calculate_somme_vendu(self):
        prix_achat = self.edit_prix_d_achat[0].text()
        prix_vente = self.edit_prix_de_vente[0].text()
        if prix_achat.isdigit() and prix_vente.isdigit():
            prix_achat = int(prix_achat)
            prix_vente = int(prix_vente)
            vendu = prix_vente * self.recup_quantite_vendu()

            self.calculate_somme_non_vendu(vendu)
            self.edit_total_vendu[0].setText(str(vendu))
            self.edit_total_vendu[0].setStyleSheet("border: 1px solid green;")
            print(vendu)

    def calculate_somme_non_vendu(self, non_vendu):
        prix_achat = self.edit_prix_d_achat[0].text()
        if prix_achat.isdigit():
            prix_achat = int(prix_achat)
            restants = int(self.edit_quantite_restants[0].text())
            total_non_vendu = prix_achat * restants
            self.edit_total_non_vendu[0].setText(str(total_non_vendu))
            self.edit_total_non_vendu[0].setStyleSheet("border: 1px solid green;")
            print(total_non_vendu)

    def show_input(self):
        print(self.sender().text()) """
