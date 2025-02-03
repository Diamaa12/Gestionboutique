from cgitb import handler

import mysql.connector
from mysql.connector import Error

class MysqlDatabase:
    def __init__(self):
        self.connection = None
    def connect(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
            return self.connection
        except Error as e:
            print(e)
            return e
    def disconnect(self):
        if self.connection:
            print("MySQL connection is closed")
            self.connection.close()

class MysqlHandler:
    def __init__(self, connection):
        self.connection = connection
    def create_produit_table(self):
        try:
            cursor = self.connection.cursor()
            sql = "CREATE TABLE IF NOT EXISTS produit (id INT AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(255), quantite INT, prix FLOAT)"
            add_column = "ALTER TABLE produit ADD COLUMN ttl_somme_vendu FLOAT GENERATED ALWAYS AS (quantite_restante * prix_achat) STORED LAST;"
            change_column = "ALTER TABLE produit CHANGE COLUMN prix quantite_vendu FLOAT;"
            cursor.execute(add_column)
            self.connection.commit()
            print("Table created successfully")
        except Error as e:
            print(e)
            return None
    def insert_produit(self, produit_name, produit_quantite, quantite_vendu, prix_achat, prix_vente):
        try:
            cursor = self.connection.cursor()
            sql = ("INSERT INTO produit (nom,  quantite, quantite_vendu,  prix_achat, prix_vente,"
                   ") VALUES (%s, %s, %s, %s, %s, %s)"
                   "RETURNING *;")
            val = (produit_name, produit_quantite, quantite_vendu, prix_achat, prix_vente)
            cursor.execute(sql, val)
            self.connection.commit()
            print("Record inserted successfully into table")
        except Error as e:
            print(e)
    def update_produit(self, produit_name, produit_quantite, quantite_vendu, quntite_restante, prix_achat, prix_vente, prix_total,
                           prix_total_non_vendu):
        try:
            cursor = self.connection.cursor()
            sql = f"UPDATE produit SET quantite = 0, quantite_vendu = 0 WHERE nom = '{produit_name}';"
            product_name = f"SELECT * FROM produit;"

            cursor.execute(product_name)
            self.connection.commit()
            print("Record updated successfully")
        except Error as e:
            print(e)
            return None
    def fetch_produits(self):
        try:
            cursor = self.connection.cursor()
            sql = "SELECT * FROM produit;"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(e)
            return None
if __name__ == '__main__':
    host = "localhost"
    user = 'phpmyadmin'
    password = 'Galle11@'
    database = 'phpmyadmin'

    produit_name = input("Entrer le nom du produit: ")
    produit_quantite = int(input("Taper le nombre de produit:"))
    quantite_vendu = int(input("Entrer la quantite vendue: "))
    quntite_restante =  produit_quantite - quantite_vendu
    prix_achat = float(input("Entrer le prix d'achat: "))
    prix_vente = float(input("Entrer le prix de vente: "))
    prix_total = 0
    prix_total_non_vendu = 0
    prix_total_celled = 0

    instance = MysqlDatabase()

    db_connect = instance.connect(host=host, user=user, password=password, database=database)
    handler = MysqlHandler(db_connect)
    handler.create_produit_table()
    handler.insert_produit(produit_name, produit_quantite, quantite_vendu,  prix_achat, prix_vente,)
    resultat = handler.fetch_produits()
    print(resultat)
    db_connect.disconnect()


