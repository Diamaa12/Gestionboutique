import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
class DatabasePostgre:
    def __init__(self):
        self.connexion = None
    def connect(self, host, port, user, password, database):
        try:
            self.connexion = psycopg2.connect(host=host, port=port, user=user, password=password, database=database)
            self.connexion.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return self.connexion
        except Exception as e:
            print(f"Erreur lors de la connection : {e}")
            return None
    def deconnect(self):
        if self.connexion:
            print('Deconnection')
            self.connexion.close()
    def execute_query(self, query):
        cursor = self.connexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query)
        return cursor.fetchall()

class DatabaseHandler:
    def __init__(self, connection):
        self.connection = connection
    def create_produit_table(self):
        try:
            cursor = self.connection.cursor()
            sql = ("CREATE TABLE IF NOT EXISTS boutique(id_produit serial PRIMARY KEY,"
                   "nom_produit VARCHAR(255) NOT NULL,"
                   "quantity_produit INT NOT NULL,"
                   "prix_achat DECIMAL(10,2) NOT NULL,"
                   "prix_vente DECIMAL(10,2) NOT NULL,"
                   "date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP "
                   )

            cursor.execute(sql)
            self.connection.commit()
            print("Table created successfully")
        except Exception as e:
            print(f"Erreur lors de la creation de la table : {e}")
            return None
    def insert_produit(self, nom, quantite, quantite_vendu,  prix_achat, prix_vente, ):
        try:
            cursor = self.connection.cursor()
            sql = ("INSERT INTO produits (nom, quantite, quantite_vendu,  prix_achat, prix_vente"
                   ") VALUES (%s, %s, %s, %s, %s) RETURNING *;")
            val = (nom, quantite, quantite_vendu,  prix_achat, prix_vente, )
            cursor.execute(sql, val)
            result = cursor.fetchall()
            self.connection.commit()
            print("Donnees inserees avec succes.")
            print(result)
        except Exception as e:
            print(f"Erreur lors de l'insertion de la ligne : {e}")
            return None
    def update_sommes(self):
        try:
            cursor = self.connection.cursor()
           # query = "INSERT INTO sommes ()"
            sql = ("UPDATE sommes "
                   "SET quantite_restant = produits.quantite - produits.quantite_vendu"
                   " FROM produits WHERE sommes.produit_id = produits.id")
            cursor.execute(sql)
        except Exception as e:
            print('Une erreur est survenue.', e)
            return None
    def sum_ttl_produits_vendue(self):
        try:
            cursor = self.connection.cursor()
            sql = ("SELECT SUM(quantite_vendu) FROM produits"
                   " GROUP BY quantite_vendu;")
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
            return result
        except Exception as e:
            print(f"Erreur lors de la somme des produits vendus : {e}")
            return None
    def update_table(self):
        try:
            cursor = self.connection.cursor()
            sql = ("ALTER TABLE produits DROP COLUMN quantite_restant;")
            cursor.execute(sql)
            self.connection.commit()
            print("Colones supprimés avec succés")
        except Exception as e:
            print(f"Erreur lors de la suppression des colonnes : {e}")
            return None
    def trigger_update(self):
        cursor = self.connection.cursor()
        sql = (
            "CREATE OR REPLACE FUNCTION update_quantite_restante() RETURNS TRIGGER AS $$"
            "BEGIN"
            "INSERT INTO produits (nom, quantite, quantite_vendu, prix_achat, prix_vente)"
        )
if __name__ == '__main__':
    host = "localhost"
    port = 5432
    user = 'postgres'
    password = 'Galle11'
    database = 'MyTest'

    produit_name = input("Entrer le nom du produit: ")
    produit_quantite = int(input("Taper le nombre de produit:"))
    quantite_vendu = int(input("Entrer la quantite vendue: "))
    quntite_restante =  produit_quantite - quantite_vendu
    prix_achat = float(input("Entrer le prix d'achat: "))
    prix_vente = float(input("Entrer le prix de vente: "))
    prix_total = 0
    prix_total_non_vendu = 0
    prix_total_celled = 0

    instance = DatabasePostgre()
    db_connect = instance.connect(host=host, port=port, user=user, password=password, database=database)
    handler = DatabaseHandler(db_connect)

    #handler.create_produit_table()
    handler.insert_produit(nom=produit_name, quantite=produit_quantite, quantite_vendu=quantite_vendu,
                           prix_achat=prix_achat, prix_vente=prix_vente,
                          )

    handler.sum_ttl_produits_vendue()
    #handler.update_table()
    handler.update_sommes()
    db_connect.close()