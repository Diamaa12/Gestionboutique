import os
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Signal, QDate, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QMessageBox, \
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from dotenv import load_dotenv

from .api.Product.resource_factory import RessourceFactory
from .api.gestion_boutique import Boutiquehandler, DatabasePostgre

def db_connector(env_path=None):
    #On recupère le données de connexion contenu dans le fichier .env
    #env_path = Path(__file__).parent.parent.parent.parent.absolute() / 'Envdir/.data_base_login'
    context = RessourceFactory.get_contexte()
    ressource = context.get_resource('.data_base_login')
    load_dotenv(dotenv_path=ressource)  # Charge les variables du .env dans les variables d'environnement
    host = os.environ.get('PG_HOST')
    port = os.environ.get('PG_PORT')
    user = os.environ.get('PG_ADMIN_USER')
    password = os.environ.get('PG_ADMIN_PASSWORD')
    database = os.environ.get('DB_NAME')
    if host and password:
        print('Connexion reussi.')
    return [host, port, user, password, database]
class AddProduitBarDialog(QDialog):
    produit_a_ajouter = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un produit")
        self.setGeometry(500, 500, 400, 150)
        # Créer le layout de la boîte de dialogue
        layout = QVBoxLayout()

        # Ajouter un QLabel et un QLineEdit pour entrer le nom du produit à ajouter
        self.add_produit_label = QLabel("Entrez le nom de produit à ajouter :", self)
        self.add_produit_line_edit = QLineEdit(self)
        self.add_produit_submit_button = QPushButton("Ajouter")

        # Ajouter les widgets dans le layout
        layout.addWidget(self.add_produit_label)
        layout.addWidget(self.add_produit_line_edit)
        layout.addWidget(self.add_produit_submit_button)


        # Connecter le bouton "Ajouter"
        self.add_produit_submit_button.clicked.connect(self.add_produit_on_submit)

        # Appliquer le layout
        self.setLayout(layout)

    def add_produit_on_submit(self):
        # Récupérer le texte du QLineEdit
        nom_du_produit = self.add_produit_line_edit.text()
        if nom_du_produit:
            confirmation = QMessageBox.question(self, "Ajouter", f"Voulez-vous vraiment ajouter le produit {nom_du_produit} ?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmation == QMessageBox.StandardButton.Yes:
                self.produit_a_ajouter.emit(nom_du_produit) # Émettre le signal avec le nom du produit
                print(f"Signal d'ajout du produit : {nom_du_produit}, et émis.")
                QMessageBox.information(self, "Ajouté", f"{nom_du_produit} ajouté avec succés. \n Redemarer l'application pour voir le produit ajouté.")
            else:
                print('Ajout annulé')
                QMessageBox.warning(self, "Annulé", f"L'ajout du produit {nom_du_produit} est annulé.")
        else:
            print("Aucun produit n'a été entré.")
        self.close()

class DeleteProduitBarDialog(QDialog):
    produit_a_supprimer = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Supprimer un produit")
        self.setGeometry(500, 500, 400, 150)
        # Créer le layout de la boîte de dialogue
        layout = QVBoxLayout()

        #Ajouter un QLabel et unQlineEdit pour entrer le nom du produit à supprimer
        self.delete_produit_label = QLabel("Entrez le nom du produit à supprimer:", self)
        self.delete_produit_line_edit = QLineEdit(self)
        self.delete_produit_submit_button = QPushButton("Supprimer")

        # Ajouter les widgets dans le layout
        layout.addWidget(self.delete_produit_label)
        layout.addWidget(self.delete_produit_line_edit)
        layout.addWidget(self.delete_produit_submit_button)

        # Connecter le bouton "Ajouter"
        self.delete_produit_submit_button.clicked.connect(self.delete_produit_on_submit)

        # Appliquer le layout
        self.setLayout(layout)

    def delete_produit_on_submit(self):
        # Récupérer le texte du QLineEdit
        nom_du_produit = self.delete_produit_line_edit.text().strip()
        if nom_du_produit:
            print(f"Signal de suppression du produit : {nom_du_produit}, et émis")
            confirmation = QMessageBox.question(self, "Supprimer", f"Voulez-vous vraiment supprimer le produit {nom_du_produit} ?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmation == QMessageBox.StandardButton.Yes:
                # On supprime le produit de la base de données
                self.api_db_postgre = DatabasePostgre()
                connexion = self.api_db_postgre.connect_to_db(*db_connector())
                instance_data = Boutiquehandler(connexion)
                instance_data.delete_product_name(nom_du_produit)
                # Émettre le signal avec le nom du produit afin que le produit soit supprimé aussi dans le fichier json
                self.produit_a_supprimer.emit(nom_du_produit)
                QMessageBox.information(self, "Supprimer", f"{nom_du_produit} supprimé avec succés.\n Redemarer l'application pour voir le produit supprimé.")
            else:
                print('Suppression annulé')
                QMessageBox.warning(self, "Annulé", f'La suppression du produit {nom_du_produit} annulé.')
        else:
            print("Aucun produit n'a été entré.")
        self.close()
class HistoriqueProduitBarDialog(QDialog):
    signal_calcul_periodique = Signal(str, QDate, QDate)  # Signal pour retourner le produit et l'intervalle de dates

    def __init__(self, produits, parent=None):
        super().__init__(parent)
        self.affichage_resultat = None
        self.setWindowTitle("Calcul Intervalle des Ventes")
        self.setGeometry(500, 250, 400, 150)
        # Layout principal
        layout = QVBoxLayout(self)

        # Sélection de produit
        self.label_produit = QLabel("Sélectionnez un produit :")
        layout.addWidget(self.label_produit)
        self.combo_produits = QComboBox(self)
        self.combo_produits.addItems(produits)
        layout.addWidget(self.combo_produits)

        # Date de début
        self.label_quantite_vendu = QLabel("Date de début :")
        layout.addWidget(self.label_quantite_vendu)
        self.date_debut = QDateEdit(self)
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate().addMonths(-1))  # Plage par défaut : 1 mois avant
        layout.addWidget(self.date_debut)

        # Date de fin
        self.label_somme_vendu = QLabel("Date de fin :")
        layout.addWidget(self.label_somme_vendu)
        self.date_fin = QDateEdit(self)
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())  # Date actuelle par défaut
        layout.addWidget(self.date_fin)

        # Bouton de validation
        self.btn_valider = QPushButton("Valider", self)
        self.btn_valider.clicked.connect(self.historique_de_calcul_pour_un_produit)
        layout.addWidget(self.btn_valider)

    def historique_de_calcul_pour_un_produit(self):
        # Récupérer les valeurs sélectionnées
        produit = self.combo_produits.currentText()
        date_debut = self.date_debut.date()
        date_fin = self.date_fin.date()
        print(f"L'interieure de la fonction pour le produit {produit} est entre {date_debut} et {date_fin}.")

        # Émettre le signal avec les données
        self.signal_calcul_periodique.emit(produit, date_debut, date_fin)

        self.api_db_postgre = DatabasePostgre()
        connexion = self.api_db_postgre.connect_to_db(*db_connector())
        instance_data = Boutiquehandler(connexion)
        data = instance_data.get_historique_vente_par_plage_horaire(produit, date_debut.toPython(), date_fin.toPython())
        if data:
            self.affichage_resultat = AfficherResultatForOneProduct(data)
            #La difference entre la fonction show(), exec() et que la fonction show() bloque la fênetre pricipale
            #au contraire la fonction exec() permet d'interargir avec la fênetre principale
            #self.affichage_resultat.show()
            self.affichage_resultat.exec()
        else:
            QMessageBox.warning(self, "Attention", f"Aucune quantité n'a été  encore vendu pour le produit '{produit}'")
            print('Aucune donnée trouvée pour la plage de dates spécifiée.')

class ShowHistoriqueQuantiteForProduct(QDialog):
    signal_historique_quantite = Signal(str)
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        # Fermer la boîte de dialogue
        #self.accept()
        self.setWindowTitle("Historique de Stock recu pour un produit")
        self.setGeometry(500, 250, 400, 150)
        # Layout principal
        layout = QVBoxLayout(self)

        # Sélection de produit
        self.label_produit = QLabel("Sélectionnez un produit :")
        layout.addWidget(self.label_produit)
        self.combo_produits = QComboBox(self)
        self.combo_produits.addItems(product)
        layout.addWidget(self.combo_produits)

        # Bouton de validation
        self.btn_valider = QPushButton("Valider", self)
        self.btn_valider.clicked.connect(self.historique_quantite_pour_un_produit)
        layout.addWidget(self.btn_valider)
    def historique_quantite_pour_un_produit(self):
        produit = self.combo_produits.currentText()
        date_ajout = QDate.currentDate()
        self.signal_historique_quantite.emit(produit)
        print(produit)
        print(type(produit))
        self.api_db_postgre = DatabasePostgre()
        connexion = self.api_db_postgre.connect_to_db(*db_connector())
        instance_data = Boutiquehandler(connexion)
        data = instance_data.show_historique_quantite_for_one_product(produit)
        if data:
            self.affichage_resultat = AfficherResultatQuantite(data)
            #self.affichage_resultat.show()
            self.affichage_resultat.exec()
        else:
            print("Le produit n'a pas un historique de vente à afficher.")
            QMessageBox.warning(self, "Erreur", f"Le produit '{produit}' n'a pas un historique de vente à afficher.")

class AfficherResultatForOneProduct(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique de vente pour un produit")
        self.setGeometry(500, 550, 500, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        #Le titre du table
        self.title = QLabel(self)
        self.layout.addWidget(self.title)
        #Création du tableau QTableWidget
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setRowCount(1)

        self.table.setHorizontalHeaderLabels(["Nom produit", "Quantite vendue", "Somme total vendue", "Date"])
        self.table.setSortingEnabled(True)

        # Masquer les numéros des lignes
        self.table.verticalHeader().setVisible(False)
        # Ajouter des options de redimensionnement
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Étendre les colonnes
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Ajuster hauteur des lignes


        self.layout.addWidget(self.table)

        if data:
            self.show_data(data)

    def show_data(self, data:list):
        # Effacer le contenu de la table avant de la remplir à nouveau
        self.table.clearContents()
        if data and isinstance(data, dict):
            print('Voir les données :', data)
            date_de_debut = data.get('date_de_debut', 'Aucune date')
            date_de_fin = data.get('date_de_fin', 'Aucune date')
            somme_total_vendu = data.get('somme_total_vendu', 'Aucune')
            #On transforme la somme en mode locale 1 000 000
            if somme_total_vendu != 'Aucune':
                somme_total_vendu = f"{somme_total_vendu:,.2f}".replace(",", " ").replace(".", ",")
                if somme_total_vendu.endswith(",00"):
                    somme_total_vendu = somme_total_vendu[:-3]
            if (date_de_debut and date_de_fin) != "Aucune date":
                date_de_debut = datetime.strptime(date_de_debut, '%Y-%m-%d')
                date_de_fin = datetime.strptime(date_de_fin, '%Y-%m-%d')
                date_de_debut = date_de_debut.strftime('%d/%m/%Y')
                date_de_fin = date_de_fin.strftime('%d/%m/%Y')
            # Prépare les données pour affichage (en vérifiant l'existence des clés)
            title = f"La quantité vendue pour le produit '{data.get('nom_produit', 'Aucun produit')}' du {date_de_debut} au {date_de_fin}"
            #produit_id = f"{data.get('id_produit', 'Aucun produit')}"
            ttl_vendu = f"{data.get('total_quantite_vendu', 'Aucun')} Kg"
            somme_ttl_vendu = f" {somme_total_vendu} FGN"
            nom_produit = f"{data.get('nom_produit', 'Aucun')}"
            #print(produit_id)
            #print(type(produit_id))
            self.title.setText(title)
            # Affiche les données dans l'interface graphique
            #self.table.setItem(0,0,QTableWidgetItem(produit_id))
            self.table.setItem(0,0,QTableWidgetItem(nom_produit))
            self.table.setItem(0,1,QTableWidgetItem(ttl_vendu))
            self.table.setItem(0,2,QTableWidgetItem(somme_ttl_vendu))
            self.table.setItem(0,3,QTableWidgetItem(f"{datetime.today().strftime('%d/%m/%Y')}"))


        else:
            # Si les données sont inexistantes ou incorrectes
            print('Données non disponibles ou incorrectes.')
            self.table.setItem(0,0,QTableWidgetItem("Inconnu"))
            self.table.setItem(0,1,QTableWidgetItem("Inconnu"))
            self.table.setItem(0,2,QTableWidgetItem("Inconnu"))
            self.table.setItem(0,3,QTableWidgetItem("Inconnu"))
        #Ajuster la taille des colonnes
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

class AfficherResultatQuantite(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tableau de Stockage")
        self.setGeometry(500, 550, 500, 300)

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Création du tableau QTableWidget
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Quantité reçu en Kg/Unité ", "Date"])
        self.table.setSortingEnabled(True)  # Activer le tri des colonnes

        # Ajouter des options de redimensionnement
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Étendre les colonnes
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Ajuster hauteur des lignes


        self.layout.addWidget(self.table)

        # Remplir le tableau avec les données si elles sont disponibles
        if data:
            self.show_resultat(data)

    def adjust_table_size(self, event):
        """
        Ajuste dynamiquement la taille du tableau à celle de la fenêtre.
        """
        self.table.setGeometry(self.rect())  # Redimensionne le tableau pour remplir la fenêtre
    def show_resultat(self, data):
        """
        Remplit le tableau avec les données.
        """
        self.table.setRowCount(len(data))  # Définir le nombre de lignes

        # Insérer les données
        for row_index, row in enumerate(data):
            quantite = str(row.get('historique_quantite', 'Aucune'))
            date = str(row.get('date', 'Aucune'))
            if (quantite and date) != 'Aucune':
                # Tenter de convertir la date en format attendu
                try:
                    # Si la date contient une heure, ignorer l'heure et se concentrer uniquement sur la date
                    date_object = datetime.strptime(date.split()[0], '%Y-%m-%d')
                    date = date_object.strftime('%d/%m/%Y')
                    #On ajoute le "Le" à la date.
                    date = f"Le {date}"
                except ValueError:
                    # Gestion des erreurs (si la date n'est pas dans le bon format)
                    date = "Format Invalide"
                self.table.setItem(row_index, 0, QTableWidgetItem(quantite))
                self.table.setItem(row_index, 1, QTableWidgetItem(date))
            else:
                print("quantite ou date inconnue.")
                self.table.setItem(row_index, 0, QTableWidgetItem("Aucune"))
                self.table.setItem(row_index, 1, QTableWidgetItem("Aucune"))

        # Ajuster la taille des colonnes
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
