import itertools

from .constants import *

import json
class GestionPrixQauntite:
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
        except OSError as e:
            return f"Une erreur s'est produite lors de la tentative d'écriture du fichier : {e}"

    def data_product_manager(self):
        recup_data_prix_dachat = self.json_file_reader(PATH_BUYED_PRICE_PER_UNITE)
        recup_data_prix_de_vente = self.json_file_reader(PATH_CELL_PRICE_PER_UNITE)

        recup_data_quantite_restant = self.json_file_reader(PATH_NO_BOYED_PRODUCT)
        recup_data_quantite_vendu = self.json_file_reader(PATH_BOYED_PRODUCT)

        recup_data_somme_for_one_item = self.json_file_reader(PATH_TTL_SOMME_FOR_ANY_UNITE)
        recup_data_somme_not_celled_items = self.json_file_reader(PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM)

        quantite_vendu = [item for item in recup_data_quantite_vendu.values()]
        quantite_restant = [item for item in recup_data_quantite_restant.values()]

        prix_dachat_quantite = [price for price in recup_data_prix_dachat.values()]
        prix_de_vente = [price for price in recup_data_prix_de_vente.values()]

        print(f"Prix achat unite {prix_dachat_quantite}, Prix de vente par unite {prix_de_vente}")
        print("Q restant: ", quantite_restant, "Q vendu: ", quantite_vendu)
        ttl_vendu = [(q_vendu * p_vente) for (q_vendu, p_vente) in itertools.zip_longest(quantite_vendu, prix_de_vente)]
        ttl_restant = [(q_restant * p_dachat) for (q_restant, p_dachat) in itertools.zip_longest(quantite_restant, prix_dachat_quantite)]
        print('Restant: ', ttl_restant, "Vendu: ", ttl_vendu)
        #on inscrit la somme totale vendue pour chaque produit dans le fichier json
        for keys, item in zip(recup_data_somme_for_one_item.keys(), ttl_vendu):
            recup_data_somme_for_one_item[keys] = item
        for keys, item in zip(recup_data_somme_not_celled_items.keys(), ttl_restant):
            recup_data_somme_not_celled_items[keys] = item
        self.json_file_writer(PATH_TTL_SOMME_FOR_ANY_UNITE, recup_data_somme_for_one_item)
        self.json_file_writer(PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM, recup_data_somme_not_celled_items)
    def somme_ttl_produits_vendue(self):
        somme_ttl_vendu = self.json_file_reader(PATH_TTL_SOMME_FOR_ALL_CELLED_PRODUCT)
        somme_ttl_for_every_product = self.json_file_reader(PATH_TTL_SOMME_FOR_ANY_UNITE)
        sommes_list = [somme for somme in somme_ttl_for_every_product.values()]
        sommettl = 0
        for somme in sommes_list:
            sommettl += somme
        somme_ttl_vendu['sommes'] = sommettl
        self.json_file_writer(PATH_TTL_SOMME_FOR_ALL_CELLED_PRODUCT, somme_ttl_vendu)
        return sommettl
    def recup_somme_vendu(self, produit_name):
        somme_vendu = self.json_file_reader(PATH_TTL_SOMME_FOR_ANY_UNITE)
        vendue = somme_vendu[produit_name]
        print(vendue)
        return vendue
    def recup_somme_restant(self, produit_name):
        somme_restante = self.json_file_reader(PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM)
        restant = somme_restante[produit_name]
        print(restant)
        return restant

if __name__ == '__main__':
    instance = GestionPrixQauntite()
    instance.data_product_manager()
    instance.somme_ttl_produits_vendue()