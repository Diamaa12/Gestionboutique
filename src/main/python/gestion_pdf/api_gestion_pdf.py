import os
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
class PdfGenerator:
    def __init__(self, fichier_pdf, titre, paragraph):
        self.fichier_pdf = fichier_pdf
        self.title = titre
        self.paragraph = paragraph

        self.directory = "PDFS"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.destination = os.path.join(self.directory, self.fichier_pdf)

        self.pdf = SimpleDocTemplate(self.destination, pagesize=letter)

        self.style = getSampleStyleSheet()

        self.table_title = Paragraph(self.title, self.style["Heading1"])
        self.table_paragraph = Paragraph(self.paragraph, self.style["BodyText"])

        self.spacer = Spacer(1, 12)
    def create_pdf(self, data):

        #Création du table
        table = Table(data)
        #Mise à forme du tableau
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12)]))
        #Nueancé les couleurs de colonnes
        for i in range(1, len(data)):
            if i % 2 == 0:
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)]))
            table_elements = [
                self.table_title,
                self.spacer,
                self.table_paragraph,
                self.spacer,
                table
            ]
            try:
                self.pdf.build(table_elements)
                print(f"Le cocument: {self.fichier_pdf} a été crée avec succés. ")
                return True
            except PermissionError as e:
                print(f"Erreur de permission: {e}")
                return False
            except Exception as e:
                print(f"Une erreur inattendue est survenue: {e}")
                return False


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
    #pdf_generation()
    produuit_names = ['Poulets', 'Dindes', 'Pattes']
    produits = [
        [item for item in produuit_names],
        ['id', 'nom', 'quantite', 'prix_achat', 'prix_vente'],
        [1, 'Poulets', 10, 100, 150],
    ]

    titre = "Tableau des produits"
    paragraph = "Cette liste contient le nom la quantité le prix d'achat et le prix de vente d'un produit"
    pdf_file_name = "my_prodcut_pdf.pdf"
    pdf_generator = PdfGenerator(pdf_file_name, titre, paragraph)
    pdf_generator.create_pdf(produits)