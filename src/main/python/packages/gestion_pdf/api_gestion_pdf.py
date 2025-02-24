import os
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from pydoc import describe

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,  Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet

#from src.main.python.packages.api.gestion_boutique import Boutiquehandler, DatabasePostgre
#from src.main.python.packages.leyssare_tech import db_connector


class PdfGenerator:
    def __init__(self):

        self.directory = Path.home() / "Desktop/PDF Documents"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.date_ajout = datetime.now().strftime("%d/%m/%Y")
        self.spacer = Spacer(1, 12)

    def create_pdf_for_produit_table(self, table_product_data):

        title = "Tableau des produits"
        paragraph = "Cette liste contient le nom la quantité le prix d'achat et le prix de vente d'un produit"
        pdf_table_produit_name = "table_de_produit.pdf"

        destination = os.path.join(self.directory, pdf_table_produit_name)
        self.pdf = SimpleDocTemplate(destination, pagesize=letter)


        style = getSampleStyleSheet()

        table_title = Paragraph(title, style["Heading1"])
        table_paragraph = Paragraph(paragraph, style["BodyText"])

        product_names = []
        quantites = []
        prix_achats = []
        prix_ventes = []
        date_ajout = []
        for items in table_product_data:
            print(items[1])
            product_names.append(items[1])
            quantites.append(items[2])
            prix_achats.append(self.format_monnaie(float(items[3])))
            prix_ventes.append(self.format_monnaie(float(items[4])))
            date_ajout.append(items[5].strftime("%d/%m/%Y"))
        # print(product_names, quantites, prix_achats, prix_ventes, date_ajout)
        product_data = {"Nom_produit": product_names, "quantite": quantites, "prix_achat": prix_achats,
                        "prix_vente": prix_ventes, "date_ajout": date_ajout}

        #Implementer les données
        produit_names = product_data["Nom_produit"]
        quantites = product_data["quantite"]
        prix_achats = product_data["prix_achat"]
        prix_ventes = product_data["prix_vente"]
        #date_ajout = data["date_ajout"'']

        header_table = ['Produits'] + produit_names + ['Date d\'ajout']
        rows_table = [
            ["Quantité"] + quantites + [self.date_ajout],
            ["Prix d'achat"] + prix_achats,
            ["Prix de vente"] + prix_ventes,
        ]
        #Ajout du Tableau dans le PDF
        table_data = [header_table] + rows_table

        # Construit les données pour le tableau


        #Création du table
        table = Table(table_data, hAlign="LEFT")
        #Mise à forme du tableau
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold', colors.blueviolet),
            ("FONTNAME", (0, 1), (-1, 0), "Helvetica", colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12)]))
        #Nueancé les couleurs de colonnes
        for i in range(1, len(product_data)):
            if i % 2 == 0:
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)]))
            table_elements = [
                table_title,
                self.spacer,
                table_paragraph,
                self.spacer,
                table
            ]
            try:
                self.pdf.build(table_elements)
                print(f"Le cocument: {pdf_table_produit_name} a été crée avec succés. ")
                return True
            except PermissionError as e:
                print(f"Erreur de permission: {e}")
                return False
            except Exception as e:
                print(f"Une erreur inattendue est survenue: {e}")
                return False

    def create_pdf_for_vente_table(self, data):
        title = "Tableau des ventes"
        paragraph = "Cette liste nous permet de voir les ventes de chaque produit"

        pdf_table_vente_name = "table_de_ventes.pdf"

        destination = os.path.join(self.directory, pdf_table_vente_name)
        pdf = SimpleDocTemplate(destination, pagesize=letter)

        style = getSampleStyleSheet()

        table_title = Paragraph(title, style["Heading1"])
        table_paragraph = Paragraph(paragraph, style["BodyText"])

        produit_names = []
        quantites_vendu = []
        date_vente = []
        for item in data:
            #print(item[0], item[1], item[2])
            produit_names.append(item[0])
            quantites_vendu.append(item[1])
            date_vente.append(item[2].strftime("%d/%m/%Y"))
        print(produit_names,"\n", quantites_vendu, "\n", date_vente)
        #Mise en forme du tableau PDF
        #On crée une ligne pour le table avec la fonction zip
        rows_table = list(zip(produit_names, quantites_vendu, date_vente))
        #On crée un entête du tableau
        header_table = ["Produits", 'Quantités vendues', 'Date de vente']

        #Ajout de données dans le tableau pdf
        table_data = [header_table] + rows_table

        #Instentiation du Tableau.
        pdf_table = Table(table_data, hAlign="LEFT", colWidths=[150, 125, 175])
        #Mise en forme du tableau
        pdf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold', colors.blueviolet),
            ("FONTNAME", (0, 1), (-1, 0), "Helvetica", colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12)]))
        #Impression de données dans le fichier PDF
        table_elements = [
            table_title,
            self.spacer,
            table_paragraph,
            self.spacer,
            pdf_table
        ]
        try:
            pdf.build(table_elements)
            print(f"Le cocument: {pdf_table_vente_name} a été crée avec succés. ")
            return True
        except PermissionError as e:
            print(f"Erreur de permission: {e}")
            return False
        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")
            return False
    def create_pdf_for_table_sommes(self, data):
        title = "Tableau de sommes des ventes"
        paragraph = "Cette liste nous permet de voir la somme total vendu de chaque produit"

        pdf_table_somme_name = "table_de_sommes.pdf"

        destination = os.path.join(self.directory, pdf_table_somme_name)
        pdf = SimpleDocTemplate(destination, pagesize=letter)
        style = getSampleStyleSheet()

        table_title = Paragraph(title, style["Heading1"])
        table_paragraph = Paragraph(paragraph, style["BodyText"])

        nom_produit = []
        ttl_somme_vendu_pour_chaque_produit = []
        ttl_somme_restante_pour_chaque_produit = []
        date_ajout = []

        for items in data:
            nom_produit.append(items[0])
            ttl_somme_vendu_pour_chaque_produit.append(self.format_monnaie(float(items[1])))
            ttl_somme_restante_pour_chaque_produit.append(self.format_monnaie(float(items[2])))
            date_ajout.append(items[3].strftime("%d/%m/%Y"))
        print(nom_produit, ttl_somme_vendu_pour_chaque_produit, ttl_somme_restante_pour_chaque_produit, date_ajout)

        rows_table = list(zip(nom_produit, ttl_somme_vendu_pour_chaque_produit, ttl_somme_restante_pour_chaque_produit, date_ajout))
        header_table = ["Nom de produit", "Total somme vendu", "Total somme non vendu", "Date d'ajout"]

        table_data = [header_table] + rows_table

        pdf_table = Table(table_data, hAlign="LEFT")
        pdf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold', colors.blueviolet),
            ("FONTNAME", (0, 1), (-1, 0), "Helvetica", colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12)]))
        table_elements = [
            table_title,
            self.spacer,
            table_paragraph,
            self.spacer,
            pdf_table
        ]
        try:
            pdf.build(table_elements)
            print(f"Le cocument: {pdf_table_somme_name} a été crée avec succés. ")
            return True
        except PermissionError as e:
            print(f"Erreur de permission: {e}")
            return False
        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")
    def create_pdf_for_table_restants(self, data):
        title = "Tableau des restants"
        paragraph = "Cette liste nous permet de voir les restants de chaque produit"
        pdf_table_restants_name = "table_de_restants.pdf"

        destination = os.path.join(self.directory, pdf_table_restants_name)

        pdf = SimpleDocTemplate(destination, pagesize=letter)
        style = getSampleStyleSheet()

        table_title = Paragraph(title, style["Heading1"])
        table_paragraph = Paragraph(paragraph, style["BodyText"])

        nom_produit = []
        restant_pour_chaque_produit = []
        date_ajout = []
        for items in data:
            nom_produit.append(items[0])
            restant_pour_chaque_produit.append(items[1])
            date_ajout.append(items[2].strftime("%d/%m/%Y"))
        rows_table = list(zip(nom_produit, restant_pour_chaque_produit, date_ajout))
        header_table = ["Nom de produit", "Quantité restante pour chaque produit", "Date d'ajout"]

        table_data = [header_table] + rows_table

        pdf_table = Table(table_data, hAlign="LEFT")

        pdf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold', colors.blueviolet),
            ("FONTNAME", (0, 1), (-1, 0), "Helvetica", colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ]))
        table_elements = [
            table_title,
            self.spacer,
            table_paragraph,
            self.spacer,
            pdf_table
        ]
        try:
            pdf.build(table_elements)
            print(f"Le cocument: {pdf_table_restants_name} a été crée avec succés. ")
            return True

        except PermissionError as e:
            print(f"Erreur de permission: {e}")
            return False

        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")
    def create_pdf_for_table_historique_ventes(self, data):
        title = "Tableau des historiques des ventes"
        paragraph = "Historique des ventes effectué "
        pdf_table_historique_ventes_name = "table_historique_ventes.pdf"

        destination = os.path.join(self.directory, pdf_table_historique_ventes_name)

        pdf = SimpleDocTemplate(destination, pagesize=letter)
        style = getSampleStyleSheet()

        table_title = Paragraph(title, style["Heading1"])
        table_paragraph = Paragraph(paragraph, style["BodyText"])

        nom_produit = []
        quantite_vendues = []
        date_ajout = []
        for items in data:
            nom_produit.append(items[0])
            quantite_vendues.append(items[1])
            date_ajout.append(items[2].strftime("%d/%m/%Y"))
        rows_table = list(zip(nom_produit, quantite_vendues, date_ajout))
        header_table = ["Nom de produit", "Historique des ventes", "Date d'ajout"]

        table_data = [header_table] + rows_table

        pdf_table = Table(table_data, hAlign="LEFT", colWidths=[150, 125, 175])

        pdf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold', colors.blueviolet),
            ("FONTNAME", (0, 1), (-1, 0), "Helvetica", colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ]))
        table_elements = [
            table_title,
            self.spacer,
            table_paragraph,
            self.spacer,
            pdf_table
        ]
        try:
            pdf.build(table_elements)
            print(f"Le cocument: {pdf_table_historique_ventes_name} a été crée avec succés. ")
            return True

        except PermissionError as e:
            print(f"Erreur de permission: {e}")
            return False

        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")
    def create_pdf_for_table_historique_product_quantite(self, data):
        title = "Tableau des historiques des produits et quantites"
        paragraph = "Historique des produits et quantites"
        pdf_table_historique_produit_quantite_name = "historique_de_quantite_recu.pdf"

        destination = os.path.join(self.directory, pdf_table_historique_produit_quantite_name)

        pdf = SimpleDocTemplate(destination, pagesize=letter)
        style = getSampleStyleSheet()

        table_title = Paragraph(title, style["Heading1"])
        table_paragraph = Paragraph(paragraph, style["BodyText"])

        nom_produit = []
        historique_quantite_ressu = []
        date_ajout = []
        for items in data:
            nom_produit.append(items[0])
            historique_quantite_ressu.append(items[1])
            date_ajout.append(items[2].strftime("%d/%m/%Y"))
        rows_table = list(zip(nom_produit, historique_quantite_ressu, date_ajout))
        header_table = ["Nom de produit", "Historique quantité recu", "Date d'ajout"]

        table_data = [header_table] + rows_table

        pdf_table = Table(table_data, hAlign="LEFT", colWidths=[150, 125, 175])

        pdf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold', colors.blueviolet),
            ("FONTNAME", (0, 1), (-1, 0), "Helvetica", colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ]))
        table_elements = [
            table_title,
            self.spacer,
            table_paragraph,
            self.spacer,
            pdf_table
        ]
        try:
            pdf.build(table_elements)
            print(f"Le cocument: {pdf_table_historique_produit_quantite_name} a été crée avec succés. ")
            return True

        except PermissionError as e:
            print(f"Erreur de permission: {e}")
            return False

        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")
    def test_create_pdf(self, data):
        print(data['Nom_produit'])
        print(data['quantite'])
        print(data['prix_achat'])
        print(data['prix_vente'])
        print(data['date_ajout'])
        return True

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
def pdf_generation():
    title = "Bismillahi Arahman Arrahim!"
    contenu = "Dans cette petit fichier nous allons tester le fonctionnement de Reportlab"

    directory = "PDFS"
    directory = os.path.join(directory)
    if os.path.exists(directory):
        print(f"Un fichier nommé {directory} existe dèjà.")
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            print("Creation of the directory %s failed" % directory)
            return
    if not os.path.exists(directory) and not os.access(directory, os.W_OK):
        print("Permission pour crée:  %s refusé" % directory)
        return
    #Génération du PDF.
    try:
        destination = os.path.join(directory, "my_first_file.pdf")
        # Definir les donnés du tableau
        fichier = os.path.join(directory, "my_table_names.pdf")

        my_files = canvas.Canvas(destination, pagesize=letter)
        dest = SimpleDocTemplate(fichier, pagesize=letter)

        my_files.setFillColorRGB(0.1, 0.5, 1)
        my_files.setFont("Helvetica-Bold", 12)
        my_files.drawString(100, 750, title)


        my_files.setFillColor(colors.darkred)
        my_files.setFont("Helvetica", 10)
        my_files.drawString(100, 725, contenu)



        titre = 'Liste des membres du bureau'
        paragraph = "Cette liste contient les membres du bureau"

        styleSheet = getSampleStyleSheet()
        title_style = styleSheet["Heading1"]
        paragraph_style = styleSheet["BodyText"]

        titre = Paragraph(titre, title_style)
        paragraph = Paragraph(paragraph, paragraph_style)
        #Définir la largeur et la hauteur
        spacer = Spacer(1, 12)


        table_perso = [
            ['Id', 'Nom', 'Prenom', 'Age', "Adresse"],
            [1, "Bassir", 'Diallo', 23, '42779 Haan'],
            [2, "Alpha", 'Barry', 20, '4277 Neuss'],
            [3, "Saliou", 'Diallo', 34, '50891 Opladen']
        ]

        # Générer le fichier PDF avec une structure de base
        #pdf = SimpleDocTemplate(destination, pagesize=letter)

        #Création du tableau
        table = Table(table_perso)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12)
        ]))
        # Ajouter une alternance de couleurs pour les lignes (zebra stripes)
        for i in range(1, len(table_perso)):
            if i % 2 == 0:  # Lignes paires en gris clair
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                ]))
            # Générer le fichier PDF
            elements = [
                titre, #Ajouter le titre
                spacer, #Espace entre le titre et le paragraph
                paragraph, #Ajout du paragraph
                spacer, #Espace entre le paragraph et le tableau
                table]  # Liste des éléments à écrire dans le PDF
            dest.build(elements)

        my_files.save()
        print("Creation du fichier pedf")
    except PermissionError as e:
        print('Permission refusé', e)
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    pass
   #pdf_generation()
   #connect_to_db = api_db_postgre = DatabasePostgre()
   #connect = connect_to_db.connect_to_db(*db_connector())

   #product_manager = Boutiquehandler(connect)

   #table_product_data = product_manager.show_table_produit()
   #table_vente_data = product_manager.show_table_vente()
   #table_somme_data = product_manager.show_table_sommes()
   #table_restants_data = product_manager.show_table_restant()
   #table_historique_ventes_data = product_manager.show_table_historique_ventes()
   #table_historique_product_quantite = product_manager.show_table_historique_product_quantite()





   #pdf_generator = PdfGenerator()

   #pdf_generator.create_pdf_for_produit_table(table_product_data)
   #pdf_generator.create_pdf_for_vente_table(table_vente_data)
   #pdf_generator.create_pdf_for_table_sommes(table_somme_data)
   #pdf_generator.create_pdf_for_table_restants(table_restants_data)
   #pdf_generator.create_pdf_for_table_historique_ventes(table_historique_ventes_data)
   #pdf_generator.create_pdf_for_table_historique_product_quantite(table_historique_product_quantite)