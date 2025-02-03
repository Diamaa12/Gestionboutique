import itertools
import os
import json
import pathlib


#from distutils.command.install import quantite

from .constants import JSON_FILES, PATH_PRODUCT_NAME, PATH_BOYED_PRODUCT, PATH_NO_BOYED_PRODUCT, PATH_PRODUIT_DISPO_OR_FINISH


class GestionQuantite:
    new_quantite = False
    restant = 0
    @property
    def chemin_json(self, json_file_name="quantite_dispo"):
        return os.path.join(JSON_FILES, json_file_name + '.json')

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

    def quantite_no_vendue(self, quantite_dispo, quantite_vendu):
        differences = self.json_file_reader(PATH_PRODUCT_NAME)
        restant = self.json_file_reader(PATH_NO_BOYED_PRODUCT)
        dict_valeurs = list(differences.values())
        #if len(dict_valeurs) != len(quantite_vendu):
        #    print('Les les longuers de la liste est diffents du longuer de dictionnaire quantite')
        #    return None
        #dict_valeurs.sort()
        #quantite_vendu.sort()
        if dict_valeurs == quantite_dispo:
            keys = [key for key in restant.keys()]
            print(keys)
            for compteur, (v_dispo, v_vendu) in enumerate(zip(quantite_dispo, quantite_vendu)):
                non_vendu = v_dispo - v_vendu
                print(f'Le nombre restant {keys[compteur]} est de: {non_vendu}')
                restant[keys[compteur]] = non_vendu
        else:
            print('Les Longuer sont différents')
            return None
        self.json_file_writer(PATH_NO_BOYED_PRODUCT, restant)
        return restant

    def gestion_produit_non_vendue(self, quantite_dispo, quantite_vendu, produit_name):
        porduit_non_vendue = self.json_file_reader(PATH_NO_BOYED_PRODUCT)
        # on verifi que la difference entre produitvendu et produidispo n'est pas negatif
        restant = quantite_dispo - quantite_vendu
        if restant >= 0:
            porduit_non_vendue[produit_name] = restant
            self.json_file_writer(PATH_NO_BOYED_PRODUCT, porduit_non_vendue)
        else:
            print('Le stock est fini')
    def print_produit_restant(self, produit_name):
        restant_dict = self.json_file_reader(PATH_NO_BOYED_PRODUCT)
        print(produit_name, restant_dict[produit_name])
        restant = restant_dict[produit_name]
        return restant
    def retourne_quantite_restant(self):
        restant_dict = self.json_file_reader(PATH_NO_BOYED_PRODUCT)
        return restant_dict.values()
    def increment_quantite_vendu(self, produit_name, new_quantite_vendu):
        #On recupère les produits vendu
        print('la fonction demare')
        quantite_deja_vendue = self.json_file_reader(PATH_BOYED_PRODUCT)
        # On recupére la quantité de produits disponible
        quantite_disponible = self.json_file_reader(PATH_PRODUCT_NAME)
        """On recupére le fichier contenant le dictionnaire à valeur boolean"""
        produit_finish_dict = self.json_file_reader(PATH_PRODUIT_DISPO_OR_FINISH)
        #new_quantite_vendu = []
        #On verifi si le nom du produit entré est égal au nom du produit dans le dictionnaire
        if produit_name in quantite_deja_vendue.keys():
            print(produit_name, quantite_deja_vendue[produit_name])
            # On verifi de nouveau si le nom de produit est present dans le stock
            if produit_name in quantite_disponible.keys():
                print(quantite_disponible[produit_name])
                q_dispo = int(quantite_disponible[produit_name])
                q_vendu = int(quantite_deja_vendue[produit_name])
                q_new = int(new_quantite_vendu)
                new_value = q_vendu + q_new
                if q_dispo >= new_value:

                    quantite_deja_vendue[produit_name] = new_value
                    self.json_file_writer(PATH_BOYED_PRODUCT, quantite_deja_vendue)
                    #on appel la fonction qui gere qui note la quantite non vendu de chaque produit
                    self.gestion_produit_non_vendue(q_dispo, new_value, produit_name)
                elif q_dispo <= new_value:
                    print('le produit est épuisé')
                    #Si la quantité du produit est égal à zéro

                    print(produit_name, 'est fini')
                    # on recherche le nom du produit vendu à 100% et on remet sa valeur à 0
                    quantite_deja_vendue[produit_name] = 0
                    produit_finish_dict[produit_name] = True
                    self.json_file_writer(PATH_BOYED_PRODUCT, quantite_deja_vendue)
                    self.json_file_writer(PATH_PRODUIT_DISPO_OR_FINISH, produit_finish_dict)
        else:
            print('Le produit n est pas dans la liste de produits disponible')





       # # Récupérer les indices où les valeurs de la liste dépassent celles du dictionnaire
       # #Et on s'assure qu'on ne vend pas plus ce qu'on a de produit disponible
#
       # produit_restant = {}
       # produit_fini = []
       # # Boucle pour comparer les éléments de la liste et du dictionnaire
       # for key, val_list, val_dict in zip(quantite_dispo.keys(), total_quantite_vendu, quantite_dispo.values()):
       #     if val_list <= int(val_dict):
       #         #Si le produit n est pas encore fini, on l'ajoute au produits vendu
       #         produit_restant[key] = val_list
       #     else:
       #         #si le produit est fini, on indique au commercant que tel produit est fini
       #         #On laisse la valeur du dictionnaire comme avant
       #         #produit_restant[key] = val_dict
       #         produit_restant[key] = 0
       #         produit_fini.append(key)
       # #On regarde si y a un produit qui est fini
       # if len(produit_fini) > 0:
       #     p_finish = tuple(produit_fini)
       #     print(', '.join(map(str, p_finish)), 'est fini')
       #     return produit_fini
       # print("Données enregistré avec succés.")
       # #self.json_file_writer(PATH_BOYED_PRODUCT, produit_restant)
       # return True

    def recup_produit_name(self):
        product_name = self.json_file_reader(PATH_PRODUCT_NAME)
        product_name_list = [quantite for quantite in product_name.keys()]
        for i in product_name_list:
            print(i)
        return product_name_list

    def recup_quantite_kg_unite(self):
        quantite_unite_Kg = self.json_file_reader(PATH_PRODUCT_NAME)
        quantie_unite_kg_list = [quantite for quantite in quantite_unite_Kg.values()]
        for i in quantie_unite_kg_list:
            print(i)
        return quantie_unite_kg_list

    def recup_produit_vendue_name(self):
        produit_name = self.json_file_reader(PATH_BOYED_PRODUCT)
        produit_name_list = [key for key in produit_name.keys()]
        for i in produit_name_list:
            print(i)
        return produit_name_list

    def recup_quantite_vendue(self):
        number_produit_buyed = self.json_file_reader(PATH_BOYED_PRODUCT)
        produit_buyed_list = [quantite for quantite in number_produit_buyed.values()]
        for i in produit_buyed_list:
            print(i)
        return produit_buyed_list
    #Cette fonction permet de reinitialiser la valeur d'un produit qui est fini d'être vendu
    #à zero, avant qu'une nouvelle quantité de ce même produit ne soit disponible
    def qline_edit_desabler(self):
        produit_finish_dict = self.json_file_reader(PATH_PRODUIT_DISPO_OR_FINISH)
        return produit_finish_dict

    def add_new_quantite_kg_unite(self, product, quantite):
        print("Debut d'appel de la fonction ")
        print(product, ":", quantite)
        old_product_value = self.json_file_reader(PATH_PRODUCT_NAME)
        product_name = [name for name in old_product_value.keys()]

        """On recupére le fichier contenant le dictionnaire à valeur boolean"""
        produit_finish_dict = self.json_file_reader(PATH_PRODUIT_DISPO_OR_FINISH)

        for old_product in product_name:
            if old_product == product:
                old_product_value[old_product] = int(quantite)
                produit_finish_dict[old_product] = False
                self.new_quantite =True
                self.json_file_writer(PATH_PRODUCT_NAME, old_product_value)
                self.json_file_writer(PATH_PRODUIT_DISPO_OR_FINISH, produit_finish_dict)


    def add_item_to_celled_items(self, product, value):
        celled_items = self.json_file_reader(PATH_BOYED_PRODUCT)
        for item in celled_items.keys():
            if item == product:
                celled_items[item] = value
                self.json_file_writer(PATH_BOYED_PRODUCT, celled_items)
                print(product, ': ', value, 'viens d etre ajouter au produit vendu. ')
    def not_celled_items(self):
        quantite_disponible = self.json_file_reader(PATH_PRODUCT_NAME)
        quantite_vendu = self.json_file_reader(PATH_BOYED_PRODUCT)
        quantite_non_vendue = self.json_file_reader(PATH_NO_BOYED_PRODUCT)

        quantite_dispo_list = [item for item in quantite_disponible.values()]
        quantite_vendu_list = [item for item in quantite_vendu.values()]
        restants = []
        quantite_restant = 0
        for item1, item2 in zip(quantite_dispo_list, quantite_vendu_list):
            quantite_restant = int(item1) - int(item2)
            print('No celled item:', quantite_restant)
            restants.append(quantite_restant)
        #Ajouter le resultat dans le fichiers des produits qui ne sont pas encore vendu
        non_vendu_produits = quantite_non_vendue.keys()
        for produit, restant in zip(non_vendu_produits, restants):
            quantite_non_vendue[produit] = restant
        print(quantite_non_vendue)
        self.json_file_writer(PATH_NO_BOYED_PRODUCT, quantite_non_vendue)

        print(f'Le quantite restant de  est: {restants}')
        return restants

      #if dict_valeurs == quantite_dispo:
      #    keys = [key for key in restant.keys()]
      #    print(keys)
      #    for compteur, (v_dispo, v_vendu) in enumerate(zip(quantite_dispo, quantite_vendu)):
      #        non_vendu = v_dispo - v_vendu
      #        print(f'Le nombre restant {keys[compteur]} est de: {non_vendu}')
      #        restant[keys[compteur]] = non_vendu
      #else:
      #    print('Les Longuer sont différents')
      #    return None
      #self.json_file_writer(PATH_NO_BOYED_PRODUCT, restant)
      #return restant

    def test(self, item, produit_name):
        def handler(item, produit_name):
            print(item, 'à l produit_name: ',produit_name)
        if item:
            new_element = {produit_name:item}
            self.json_file_writer(PATH_PRODUCT_NAME, new_element)
            handler(item, produit_name)
        else:
            print('Erreur')
        #print('Fonction appeler avec succés. ', item)
if __name__ == "__main__":
    quantite_dispo_dict = {}
    quantite_vendu_dict = {}
    quantite_restant_list = []
    new_quantite_vendue_list = []

    for i in range(5):
        produit = input('Entrez le nom du produit: ')
        quantite_dispo_kg_unite = int(input(f'Entrez la quantite disponible pour {produit}: '))
        quantite_dispo_dict[produit] = quantite_dispo_kg_unite

    #quantite_vendu_kg_unite = 0
    for i in range(5):
        produit = input('Entrez le nom du produit vendue:  ')
        quantite_vendu_kg_unite = int(input(f'Entrez la quantite vendue pour {produit}: '))
        quantite_vendu_dict[produit] = quantite_vendu_kg_unite
        new_quantite_vendue_list.append(quantite_vendu_kg_unite)

    #print(GestionQuantite([], 5, 5).quantite_restant)
    q_v_l = [i for i in new_quantite_vendue_list if i is not None]
    print(q_v_l)
    class_instance = GestionQuantite()

    #On enregistre les données sur le fichiers Json
    rst1 = class_instance.json_file_writer(PATH_PRODUCT_NAME, quantite_dispo_dict)
    print(rst1)
    #rst2 = class_instance.json_file_writer(quantite_vendu_json, quantite_vendu_dict)
    #print(rst2)

    #On recupère les données du fichier json
    print('--' * 20)
    produit_name = class_instance.recup_produit_name()
    quantite_produit_dispo = class_instance.recup_quantite_kg_unite()
    print('--' * 20)
    class_instance.recup_produit_vendue_name()
    quantite_kg_unite_vendue = class_instance.recup_quantite_vendue()
    print('--' * 20)
    print(quantite_kg_unite_vendue)
    print('--' * 20)
    #ici on appel la fonction pour incrementer la valeur vendu
    product_finished = class_instance.increment_quantite_vendu(new_quantite_vendue_list)
    print('--' * 20)
    #On reaffiche la nouvelle valeur dans le fichier quantite_vendu.json
    quantite_vendu_name = class_instance.recup_produit_vendue_name()
    print('--' * 20)
    quantite_vendue_items = class_instance.recup_quantite_vendue()
    #On recupere ici les produits qui ne sont pas encore vendu
    produit_non_vendu = class_instance.quantite_no_vendue(quantite_produit_dispo, quantite_vendue_items)
    print(f'Le produit qui ne pas encore vendu{produit_non_vendu}')
    class_instance.gestion_produit_non_vendue()
    print('--' * 20)
    class_instance.reset_quantite_vendue(product_finished)
