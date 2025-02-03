import itertools
import os
import json
import pathlib

from .constants import PATH_PRODUCT_NAME, PATH_BOYED_PRODUCT, PATH_NO_BOYED_PRODUCT, PATH_TTL_SOMME_FOR_ANY_UNITE, \
    PATH_BUYED_PRICE_PER_UNITE, PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM, PATH_CELL_PRICE_PER_UNITE
from .constants import PATH_CELL_PRICE_PER_UNITE


class GestionPrix:
    def __init__(self):
        pass
    def json_file_reader(self, json_file_name):
        try:
            with open(json_file_name, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                return data
        except FileNotFoundError as e:
            return e


    def json_file_writer(self, json_file_name, data_dict):
        try:
            with open(json_file_name, 'w', encoding='utf-8') as json_file:
                json.dump(data_dict, json_file, indent=4)
        except FileNotFoundError as e:
            return e

    def recup_prix_dachat(self, valeurs:list):

        # Vérification que la liste n'est pas vide et que tous les éléments sont de type int
        if valeurs and all(isinstance(x, int) for x in valeurs):
            #recuperation du fichier json
            prix_dachat_json = self.json_file_reader(PATH_BUYED_PRICE_PER_UNITE)
            item_name = [i for i in prix_dachat_json.keys()]
            #print("Les Produit sont: ", item_name)
            #Insertion de donnés recu en liste dans le dictionnaire
            somme_total_per_unite = {item_name[i]: valeurs[i] for i in range(len(item_name))}
            print(f"Prix d'achat du produit et son nom {somme_total_per_unite}")
            #enregistrement de donnés dans le fichier json
            self.json_file_writer(PATH_BUYED_PRICE_PER_UNITE, somme_total_per_unite)
            #On retourne un dictionnaire contenant les noms de produits et leurs prix d'achat
            return somme_total_per_unite
        else:
            print("Y a un erreur ")
            return False

    def set_buyed_price_for_one_item(self, product_name, somme):
        print(product_name, somme)
        if product_name and somme:
            prix_de_vente = self.json_file_reader(PATH_BUYED_PRICE_PER_UNITE)
            prix_de_vente[product_name] = int(somme)
            self.json_file_writer(PATH_BUYED_PRICE_PER_UNITE, prix_de_vente)
            print(f"Le prix d'achat du produit {product_name} est de {somme} euros et est celled")
        else:
            print("Y a un erreur ")
            return False
    def set_celled_price_for_one_item(self, product_name, somme):
        print(somme, product_name)
        if somme:
            prix_de_vente = self.json_file_reader(PATH_CELL_PRICE_PER_UNITE)
            print(
                f"Le prix de vente du produit {product_name} est de {somme} euros et est celled"
            )
            prix_de_vente[product_name] = int(somme)
            self.json_file_writer(PATH_CELL_PRICE_PER_UNITE, prix_de_vente)
        else:
            print("Y a un erreur ")
            return False
    def recup_total_prise_for_one_item(self, valeurs:list):
        prix_unitaire = valeurs
        total_prix = self.json_file_reader(PATH_BOYED_PRODUCT)
        item_vendu = [i for i in total_prix.values()]
        item_names = [i for i in total_prix.keys()]
        #print(item_vendu, item_names)
        sommes_ttl = [prix_de_vente * qauntite_vendu for prix_de_vente, qauntite_vendu in zip(prix_unitaire, item_vendu)]
        #print(sommes_ttl)
        somme_total_per_unite = {item_names[i]: sommes_ttl[i] for i in range(len(item_names))}
        print(f"Le prix de vente totalise pour chaque produit et son nom: {somme_total_per_unite}")
        self.json_file_writer(PATH_TTL_SOMME_FOR_ANY_UNITE,somme_total_per_unite)

    def recup_total_non_vendu_price_for_one_item(self, price:list):
        non_vendu_poduct = self.json_file_reader(PATH_NO_BOYED_PRODUCT)
        prix_dachat_per_product = price
        if len(prix_dachat_per_product) != len(non_vendu_poduct):
            raise ValueError('La longuer de la list et les values du dict ne correspondent pas')
        somme = {key: prix_dachat * prix_dachat_per_product[i] for i , (key, prix_dachat) in enumerate(non_vendu_poduct.items())}
        print('TTL non Vendu {}'.format(somme))
        self.json_file_writer(PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM, somme)
if __name__ == "__main__":
    prix_dachat_quantite_kg_unite = []
    prix_de_vente_unite_kg = []

    for i in range(2):
        price = int(input(f"Entrer le prix d'achat du produit no {i} "))
        prix_dachat_quantite_kg_unite.append(price)
        prix_de_vente = int(input(f"Entrer le prix de vente du produit no {i}"))
        prix_de_vente_unite_kg.append(prix_de_vente)
    class_instance = GestionPrix()
    class_instance.recup_prix_dachat(prix_dachat_quantite_kg_unite)
    class_instance.set_buyed_price_for_one_item(prix_de_vente_unite_kg)
    class_instance.recup_total_prise_for_one_item(prix_de_vente_unite_kg)
    class_instance.recup_total_non_vendu_price_for_one_item(prix_dachat_quantite_kg_unite)
