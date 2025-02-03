from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class DialogConfirmation(QDialog):
    def __init__(self, produit_name, quantite, prix_achat, prix_vente, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmer les données")
        self.setMinimumSize(350, 225)

        # Stockage des données
        self.produit_name = produit_name
        self.quantite = quantite
        self.prix_achat = prix_achat
        self.prix_vente = prix_vente

        # Création des widgets
        self.lbl_message = QLabel(f"Voulez-vous enregistré les donnés suivants pour le produit {self.produit_name}?")
        self.label_quantite = QLabel(f"Quantité : {self.quantite}")
        self.label_prix_achat = QLabel(f"Prix d'achat : {self.prix_achat}")
        self.label_prix_vente = QLabel(f"Prix de vente : {self.prix_vente}")
        self.btn_confirmer = QPushButton("Confirmer")
        self.btn_annuler = QPushButton("Annuler")

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_message)
        layout.addWidget(self.label_quantite)
        layout.addWidget(self.label_prix_achat)
        layout.addWidget(self.label_prix_vente)

        # Layout pour boutons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_confirmer)
        button_layout.addWidget(self.btn_annuler)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connexions des boutons
        self.btn_confirmer.clicked.connect(self.accept)  # Clic sur "Confirmer" -> Méthode accept()
        self.btn_annuler.clicked.connect(self.reject)  # Clic sur "Annuler" -> Méthode reject()
    def get_confirmation(self):
        """
        Retourne True si l'utilisateur clique sur Confirmer, sinon False.
        """
        return self.exec() == QDialog.DialogCode.Accepted
