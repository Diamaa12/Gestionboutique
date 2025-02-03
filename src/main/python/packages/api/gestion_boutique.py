import logging
from datetime import datetime, date
from typing import Optional, List

import psycopg2
import psycopg2.extras
from PySide6.QtCore import Signal, QObject
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import LoggingConnection

from .product_manager import ProductManager

# Configurer le logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("PostgreSQL")

class CustomLoggingConnection(LoggingConnection):
    #La méthode verifi si y a de message de type RAISE NOTICE dans les requetes sql
    #Si tel est le cas, elle l'affiche
    def filter(self, msg, curs):
        logger.debug(f"Message envoyé depuis POSTGRESQL:{msg}")
        return super().filter(msg, curs)
class DatabasePostgre:
    def __init__(self):
        self.connexion = None
    def connect_to_db(self, host, port, user, password, database):
        try:
            self.connexion = psycopg2.connect(host=host,
                                              port=port,
                                              user=user,
                                              password=password,
                                              database=database)
            self.connexion.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            # IMPORTANT : Initialiser le LoggingConnection
            cursor = self.connexion.cursor()
            #self.connexion.initialize(logger) # Initialise avec un curseur
            return self.connexion
        except Exception as e:
            print(f"Erreur lors de la connexion : {e}")
            return None

    def deconnect(self) -> None:

        if self.connexion:
            print('Déconnexion')
            self.connexion.close()
    def execute_query(self, query):
        cursor = self.connexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query)
        return cursor.fetchall()

class Boutiquehandler(QObject,):
    '''Gestion des donnés pour la boutique'''

    #Creation d'un signal personnalisé PyQt
    qt_signal_quantite_restante = Signal(str, int)
    qt_signal_ttl_somme_vendu_pour_chaque_produit = Signal(str, float)
    qt_signal_ttl_somme_non_vendu_pour_chaque_produit = Signal(str, float)
    qt_signal_total_somme_vendues_de_tous_les_produit = Signal(float)

    def __init__(self, connexion):
        #On initialise le constructeur de QObject
        self.data_cache = {}
        super().__init__()
        self.connexion = connexion
    def insert_produit(self, nom:str, stock:int,  prix_achat:float, prix_vente:float) -> Optional[None]:
        try:
            cursor = self.connexion.cursor()
            #Inserer une nouvelle ligne ou bien mettre à jour la ligne si elle existe déjà
            #ON CONFLICTE permet de gerer en meme temps le type d'evenement qui a été declencher,
            # cette clause permet de gerer l'ajout d'un nouveau produit ou la mise à jour de ce deriner
            #si celci est de type insert la fonction INSERT sera appelé, sinon UPDATE sera appelé
            #On ajoute à stock_initial sa valeur de depart plus le nouveau quantite_produit entrée pour le produit mis à jour
            query = ("INSERT INTO produit (nom_produit, quantite_produit, prix_achat, prix_vente, date_achat, stock_initial)"
                    "VALUES (%s, %s, %s, %s,  NOW(), %s)"
                    "ON CONFLICT (nom_produit)"
                    "DO UPDATE SET "
                    "nom_produit = EXCLUDED.nom_produit,"
                    "quantite_produit = EXCLUDED.quantite_produit,"
                    "prix_achat = EXCLUDED.prix_achat,"
                    "prix_vente = EXCLUDED.prix_vente,"    
                    "date_achat = NOW(),"
                    "stock_initial = (select stock_initial from produit where nom_produit = EXCLUDED.nom_produit ) + EXCLUDED.quantite_produit;")
            #on insère stock pour quantite_produit et stock_initial de la table produit
            val = (nom, stock, prix_achat, prix_vente, stock,)
            cursor.execute(query, val)
            self.connexion.commit()
            #On inserer les donnés aussi dans la table historique_product_quantite.
            self.insert_on_historique_product_quantite(nom, stock)
            print(f"{nom} est ajouter avec succés dans le stock")
        except Exception as e:
            print(f"Erreur lors de l'insertion de la ligne : {e}")
            return None

    def insert_or_update_produit_vendu(self, nom_produit:str, new_quantite_vendu:int = 1) -> Optional[None]:
        """
        Fonction pour insérer une nouvelle vente ou mettre à jour une vente existante.
        id_produit : int : L'ID du produit vendu
        quantite : int : La quantité vendue
        """
        id_produit = self.get_product_id(nom_produit)
        #On s'assure que le produit existe
        if id_produit == 0:
            print(f"Produit {nom_produit} introuvable.")
            return None
        try:
            cursor = self.connexion.cursor()
            # 1. Vérifier si le produit existe déjà dans la table Ventes
            query_check = "SELECT id_produit FROM Ventes WHERE id_produit = %s;"
            cursor.execute(query_check, (id_produit,))
            result = cursor.fetchone()
            print(f" Le retour de fetchone(): {result}")
            print(f" Nouvelle quantite: {new_quantite_vendu}")
            if result is None:
                # 2. SI le produit n'existe pas, faire un INSERT
                query_insert = "INSERT INTO ventes (id_produit, quantite_vendu) VALUES (%s, %s);"
                cursor.execute(query_insert, (id_produit, new_quantite_vendu))
                print(f"Nouvelle vente ajoutée pour le produit ID {id_produit} avec une quantité de {new_quantite_vendu}.")
            else:
                # 3. SINON faire un UPDATE pour augmenter la quantité vendue
                query_update = f"UPDATE ventes SET quantite_vendu = quantite_vendu + {new_quantite_vendu}, date_vente = NOW() WHERE id_produit = {id_produit};"
                cursor.execute(query_update)
                print(f"Vente mise à jour pour le produit ID {id_produit}. Nouvelle quantité ajoutée : {new_quantite_vendu}.")
            #Insertion de donnés dans la table historique_ventes
            self.insert_on_historique_ventes(id_produit, new_quantite_vendu)
            #Gestion de décrementation de stock du colon qunatite_produit de la table produit
            self.decrement_stock(id_produit, new_quantite_vendu)
            #Emettre le signal de mise à jour de la table Restant
            quantite_restante = self.signal_show_quantite_restant_pour_chaque_produit(id_produit)
            self.qt_signal_quantite_restante.emit(nom_produit, quantite_restante)
            #Emettre le signal de mise à jour de la table somme pour somme ttl_vendu pour chaque produit
            ttl_somme_vendu = self.signal_show_total_somme_vendu(id_produit)
            self.qt_signal_ttl_somme_vendu_pour_chaque_produit.emit(nom_produit, ttl_somme_vendu)
            #Signal pour de mise à jour de la table somme pour somme ttl_non_vednu pour chaque produit
            ttl_somme_non_vendu = self.signal_show_total_somme_non_vendu(id_produit)
            self.qt_signal_ttl_somme_non_vendu_pour_chaque_produit.emit(nom_produit, ttl_somme_non_vendu)
            #Emettre un signal de mise à jour de ttl_somme_vendu dans la table sommes afin de recalculer
            #le ttl de sommes de tous les produit vendue
            ttl_sommes_vendu_de_tous_les_produits = self.show_ttl_sommes_vendu_de_tous_les_produit()
            self.qt_signal_total_somme_vendues_de_tous_les_produit.emit(ttl_sommes_vendu_de_tous_les_produits)

            print(f"Signal émis pour {nom_produit}")
            # 4. Valider la transaction
            self.connexion.commit()
        except psycopg2.Error as e:
            print(f"Erreur lors de l'ajout ou la mise à jour de la vente : {e}")
            if self.connexion:
                self.connexion.rollback()  # Annuler la transaction en cas d'erreur
    #insertion des donnés dans la table historique_ventes
    def insert_on_historique_ventes(self, id_produit:int, quantite_vendu:int) -> None:
        try:
            cursor = self.connexion.cursor()
            requete = "INSERT INTO historique_ventes (id_produit, quantite, date_vente) VALUES (%s, %s, NOW());"
            cursor.execute(requete, (id_produit, quantite_vendu))
            print("Données insérer avec succés dans la table historique_ventes.")
            self.connexion.commit()
        except Exception as e:
            print(f"Erreur lors de l'insertion dans la table historique_ventes : {e}")
            return None

    def insert_on_historique_product_quantite(self, nom_produit, quantite_produit):
        id_produit = self.get_product_id(nom_produit)
        if id_produit:
            try:
                cursor = self.connexion.cursor()
                requete = "INSERT INTO historique_product_quantite (id_produit, historique_quantite) VALUES (%s, %s);"
                cursor.execute(requete, (id_produit, quantite_produit))
            except Exception as e:
                print(f"Erreur lors de l'insertion dans la table historique_product_quantite : {e}")
                return None
    def get_product_id(self, product_name: str) -> int:
        """'Retourne l\'ID du produit entré en paramétre si il existe'"""

        #on récupère le tableau contenant les noms de produit dans product_manager.py
        produit_names = ProductManager()
        produits = produit_names.load_products()
        print(produits)
        product_name = product_name.strip()
        #on vérifie que le nom de produit existe dans la liste
        if not product_name in produits:
            print("Produit introuvable")
            print("Le produit n'existe pas dans le stock, ajouter le produit.")
            return 0
        try:
            cursor = self.connexion.cursor()
            sql = ("SELECT id_produit FROM produit "
                   "WHERE nom_produit = %s;")
            cursor.execute(sql, (product_name,))
            result = cursor.fetchall()
            id_produit = result[0][0]
            if id_produit:
                print(id_produit)
                return id_produit
            else:
                print("Produit introuvable")
        except Exception as e:
            print('Une erreur est survenue. produit inexistante.', e)
            return 0

    def get_historique_vente_par_plage_horaire(self, nom_produit:str, heure_debut: date, heure_fin: date) -> Optional[dict]:
        """
        Récupère l'historique des ventes pour un produit dans une plage horaire spécifique.
        :param nom_produit: Nom du produit
        :param heure_debut: Heure de début (format datetime.date attendu)
        :param heure_fin: Heure de fin (format datetime.date attendu)
        :return: Quantité totale vendue pour le produit
        """
        try:
            # Vérifier si les arguments heure_debut et heure_fin ne sont pas None
            if heure_debut is None or heure_fin is None:
                raise ValueError("Les dates de début et de fin doivent être spécifiées pour le calcul.")

            # Convertir les dates en chaînes pour SQL
            date_debut = heure_debut.strftime("%Y-%m-%d")
            date_fin = heure_fin.strftime("%Y-%m-%d")

            print(f"Plage de dates : {date_debut} à {date_fin}")

            # Récupérer l'id du produit
            id_produit = self.get_product_id(nom_produit)
            if id_produit == 0:
                print(f"Produit {nom_produit} introuvable.")
                return None

            # Connexion à la base de données et exécution de la requête
            cursor = self.connexion.cursor()

            query = f"""
            SELECT 
                    p.id_produit, 
                    COALESCE(SUM(h.quantite), 0) AS total_quantite,
                    p.prix_vente,
                    COALESCE(SUM(h.quantite), 0) * p.prix_vente AS total_vendu,
                    p.nom_produit
                FROM 
                    produit p
                LEFT JOIN 
                    historique_ventes h
                ON 
                    p.id_produit = h.id_produit
                WHERE 
                    p.id_produit = %s 
                    AND (h.date_vente::DATE BETWEEN %s AND %s)
                GROUP BY 
                    p.id_produit, p.prix_vente
                ORDER BY 
                    p.id_produit;
            """
            cursor.execute(query, (id_produit, date_debut, date_fin))
            result = cursor.fetchone()

            if result:
                # Organiser les données sous forme de dictionnaire
                data = {
                    "id_produit": result[0],
                    "total_quantite_vendu": result[1],
                    "prix_vente": result[2],
                    "somme_total_vendu": result[3],
                    "nom_produit": result[4],
                    "date_de_debut": date_debut,
                    "date_de_fin": date_fin,
                }
                return data
            else:
                print("Aucune vente trouvée pour ce produit dans la plage horaire spécifiée.")
                return None

        except Exception as e:
            print(f"Une erreur inattendue s'est produite lors de la récupération des ventes : {e}")
            return None
    def delete_product_name(self, product_name: str) -> None:
        id_produit = self.get_product_id(product_name)
        if id_produit:
            cursor = self.connexion.cursor()
            cursor.execute("DELETE FROM produit WHERE id_produit = %s RETURNING *;", (id_produit,))
            deleted_product = cursor.fetchone()
            print(f"Le produit {deleted_product} a été supprimé avec succés. ")
            self.connexion.commit()
            cursor.close()
            print(deleted_product)
            return deleted_product
        else:
            print("Produit introuvable ou inexistant.")
            return None


    def decrement_stock(self, id_produit:int, quantite_vendu:int) -> None:
        """
        Met à jour la table 'produit' en réduisant la quantité disponible
        si suffisante.
        """
        try:
            cursor = self.connexion.cursor()
            query = """
            UPDATE produit
            SET quantite_produit = quantite_produit - %s
            WHERE id_produit = %s AND quantite_produit >= %s;
            """
            cursor.execute(query, (quantite_vendu, id_produit, quantite_vendu))
            if cursor.rowcount == 0:
                print("Stock insuffisant ou produit introuvable.")
            else:
                print("Stock mis à jour avec succès.")
                print(f'Une quantité de {quantite_vendu} vient d être vendue pour le produit {id_produit}.')
            self.connexion.commit()
        except Exception as e:
            print(f"Une erreur est survenue lors de la mise à jour du stock : {e}")
            self.connexion.rollback()

    def show_produit_values(self, nom_produit: str) -> Optional[list]:
        id_produit = self.get_product_id(nom_produit)
        if not id_produit:
            return None
        try:
            cursor = self.connexion.cursor()
            sql = ("SELECT nom_produit, quantite_produit, prix_achat, prix_vente"
                   " FROM produit "
                   "WHERE id_produit = %s;")
            cursor.execute(sql, (id_produit,))
            result = cursor.fetchone()

            quantite_disponible = result[1]
            prix_achat = result[2]
            prix_vente = result[3]
            return [quantite_disponible, prix_achat, prix_vente]
        except Exception as e:
            print('Une erreur est survenue.', e)
            return 0
    def show_vente(self):
        try:
            cursor = self.connexion.cursor()
            sql = ("SELECT * FROM ventes")
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            for row in result:
                for item in row:
                    print(item)
                print(row)
            return result
        except Exception as e:
            print('Une erreur est survenue.', e)
            return None


    def signal_show_total_somme_vendu(self, id_produit: int) -> Optional[float]:
        """
        Cette méthode n'est pas une fonction appelable ailleurs dans le code.
        Mais quand un signal natif est émis
        :param id_produit:
        :return: ttl_somme_vendu
        """
        try:
            cursor = self.connexion.cursor()
            sql = ("SELECT ttl_somme_vendu FROM sommes "
                   f"WHERE id_produit = {id_produit} ")
            cursor.execute(sql)
            result = cursor.fetchone()
            somme = result[0]
            print(f"{somme}  vendu")
            return somme
        except Exception as e:
            print('Une erreur est survenue au niveau de la fonction show_ttl_somme_vendu()', e)
            return None
    def signal_show_total_somme_non_vendu(self, id_produit: int) -> Optional[float]:
        """
               Cette méthode n'est pas une fonction appelable ailleurs dans le code.
               Mais quand un signal natif est émis
               :param id_produit:
               :return: ttl_somme_non_vendu
               """
        try:
            cursor = self.connexion.cursor()
            sql = ("SELECT ttl_somme_non_vendu FROM sommes "
                   f"WHERE id_produit = {id_produit}")
            cursor.execute(sql)
            result = cursor.fetchone()
            somme = result[0]
            print(f"{somme} non vendu")
            return somme
        except Exception as e:
            print('Une erreur est survenue au niveau de la fonction show_ttl_somme_non_vendu()', e)
            return None
    def signal_show_quantite_restant_pour_chaque_produit(self, id_produit: int) -> Optional[int]:
        """
               Cette méthode n'est pas une fonction appelable ailleurs dans le code.
               Mais quand un signal natif est émis
               :param id_produit:
               :return: la quantité restante pour chaque produit
               """
        try:
            cursor = self.connexion.cursor()
            #recuperer les produits non vendus
            sql = ("SELECT quantite_restant FROM restant "
                   f"WHERE id_produit = {id_produit}")
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result[0][0])
            return result[0][0]
            #for row in result:
            #    print(row)
            #    for item in row:
            #        print(f"TTl Quantité non vendu: {item}")
        except Exception as e:
            print('Une erreur est survenue au niveaus de la fonction show_quantite_restant_pour_chaque_produit()', e)
            return None
    def show_ttl_somme_vendu_pour_chaque_produit(self, id_produit: int) -> Optional[float]:
        try:
            cursor = self.connexion.cursor()
            #recuperer les produits non vendu
            sql = ("SELECT ttl_somme_vendu FROM sommes "
                   f"WHERE id_produit = {id_produit};")

            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                for item in row:
                    print(f"TTl Quantité vendu: {item}")
            return result[0][0]
        except Exception as e:
            print('Une erreur est survenue.', e)
            return None
    def show_ttl_somme_non_vendu_pour_chaque_produit(self, id_produit: int) -> Optional[float]:
        try:
            cursor = self.connexion.cursor()
            #recuperer les produits non vendu
            sql = ("SELECT ttl_somme_non_vendu FROM sommes "
                   f"WHERE id_produit = {id_produit};")
            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                for item in row:
                    print(f"Quantité non vendu: {item}")
            return result[0][0]
        except Exception as e:
            print('Une erreur est survenue.', e)
            return None
    def show_quantite_restante(self, id_produit: int) -> Optional[int]:
        try:
            cursor = self.connexion.cursor()
            #recuperer les produits non vendu
            sql = ("SELECT quantite_restant FROM restant "
                   f"WHERE id_produit = {id_produit}")
            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                for item in row:
                    print(f"Quantité restante: {item}")
            return result[0][0]
        except Exception as e:
            print('Une erreur est survenue.', e)
            return None
    def show_ttl_sommes_vendu_de_tous_les_produit(self) -> Optional[float]:
        cursor = self.connexion.cursor()
        #On recupere la sommes des ventes pour tous les produits
        requete = """SELECT COALESCE(SUM(ttl_somme_vendu), 0) FROM sommes;"""
        cursor.execute(requete)
        result = cursor.fetchone()
        print("Somme vendue de tous les produit: ", result[0])
        return result[0]
    def show_historique_quantite_for_one_product(self, product_name:str) -> Optional[list]:
        id_produit = self.get_product_id(product_name)
        print(id_produit)
        print(type(id_produit))
        if id_produit:
            try:
                cursor = self.connexion.cursor()
                sql = ("SELECT historique_quantite, date "
                       "FROM historique_product_quantite "
                       "WHERE id_produit = %s "
                       " order by date desc;")
                cursor.execute(sql, (id_produit,))
                result = cursor.fetchall()
                #On construit manuellement le dictionnaire ici.
                columns = [desc[0] for desc in cursor.description]
                print(columns)
                resultat_dict = [dict(zip(columns, row)) for row in result]
                print(resultat_dict)
                if resultat_dict:
                    return resultat_dict
                else:
                    return None
            except Exception as e:
                print("L'erreur suivante est survenue: ", e)
                return None

def place_stock_save(product_name='', quantite=0, prix_achat=0.0, prix_vente=0.0):
    list_produit = []
    list_quantite = []
    list_prix_achat = []
    list_prix_vente = []
    list_produit.append(product_name)
    list_quantite.append(quantite)
    list_prix_achat.append(prix_achat)
    list_prix_vente.append(prix_vente)

    return [list_produit, list_quantite, list_prix_achat, list_prix_vente]
def place_stock():
    list_produit = ['Dindes']
    list_quantite = []
    list_prix_achat = []
    list_prix_vente = []

    for i in range(len(list_produit)):
        while True:
            try:
                quantite = int(input(f"Taper quantite ou kg pour  {list_produit[i]}: "))
                list_quantite.append(quantite)
                break
            except ValueError:
                print(f"Veuillez entrer un nombre entier valide pour {list_produit[i]}.")

    for i in range(len(list_produit)):
        while True:
            try:
                prix = float(input(f"Entrer le prix d'achat pour {list_produit[i]}: "))
                list_prix_achat.append(prix)
                break
            except ValueError:
                print(f"Veuillez entrer un prix valide pour {list_produit[i]}.")

    for i in range(len(list_produit)):
        while True:
            try:
                prix = float(input(f"Entrer le prix de vente de {list_produit[i]}: "))
                list_prix_vente.append(prix)
                break
            except ValueError:
                print(f"Veuillez entrer un prix valide pour {list_produit[i]}.")

    return [list_produit, list_quantite, list_prix_achat, list_prix_vente]
def place_stock_vendu(handler):

    produit_name = input("Entrer le nom du produit à vendre: ").strip()
    query = f"SELECT id_produit FROM produit WHERE nom_produit = %s;"
    #cursor = handler.connexion.cursor()
    cursor = handler.connexion.cursor()
    cursor.execute(query, (produit_name,))
    produit = cursor.fetchone()
    if produit:
        id_produit = produit[0]
        print(f"Produit trouvé {produit} ")
        quantite_vendu = int(input("Taper le nombre de produit vendu:"))
        print(f"{quantite_vendu} KG ou Unité vient d'être vendu pour le produit {produit_name}")
        return [id_produit, quantite_vendu]
    else:
        print("Produit introuvable")
        return None




if __name__ == '__main__':
    host = "localhost"
    port = 5432
    user = 'postgres'
    password = 'Galle11'
    database = 'gestion_stock'

    #stock = place_stock()

    instance = DatabasePostgre()
    db_connect = instance.connect_to_db(host=host, port=port, user=user, password=password, database=database)

    handler = Boutiquehandler(db_connect)
    #handler.get_product_id('Dindes')
    #Inserer la vente pour un produit
    #vendre = place_stock_vendu(handler)
   #product_items = place_stock()
   #for nom_produit, quantite_produit, prix_achat, prix_vente in zip_longest(*product_items, fillvalue='Pas de valeur'):
   #    print(nom_produit, quantite_produit, prix_achat, prix_vente)
   #    handler.insert_produit(nom=nom_produit, stock=quantite_produit,  prix_achat=prix_achat, prix_vente=prix_vente)
   ##handler.insert_or_update_produit_vendu(id_produit=vendre[0], new_quantite_vendu=vendre[1])
    #Afficher le contenu des tables
    #handler.show_produit()
    #handler.show_vente()
    #Afficher les quantités vendu total pour chaque produit
    #handler.show_quantite_restant_pour_chaque_produit()
    #handler.show_quantite_vendu_pour_chaque_produit()
    print("-"*20)
    #Afficher la quantite vendu et non vendu pour le produit vendre[0]
    #handler.show_quantite_restante(vendre[0])
    #handler.show_quantite_vendu(vendre[0])
    print("-" * 20)
    #Afficher les sommes vendu et non vendu
    #handler.show_total_somme_vendu(vendre[0])
    #handler.show_total_somme_non_vendu(vendre[0])
    print("-" * 20)
    produit = input('Donner le nom du produit:')
    handler.delete_product_name(produit)
    db_connect.close()
