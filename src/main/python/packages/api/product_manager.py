import json
from pathlib import Path

PRODUCT_JSON_FILE = Path(__file__).parent.joinpath("Product/base/products.json")
class ProductManager:
    def __init__(self, json_file=PRODUCT_JSON_FILE):
        # Nom du fichier JSON
        self.json_file = json_file

        # Charger les noms de produits depuis le fichier JSON si existant
        self.product_names = self.load_products()

    def save_products(self):
        """
        Enregistre la liste des produits dans un fichier JSON.
        """
        try:
            with open(self.json_file, "w") as file:
                json.dump(self.product_names, file, indent=4)
            print(f"Produits enregistrés dans {self.json_file}.")
        except Exception as e:
            print(f"Erreur lors de l'enregistrement des produits : {e}")

    def load_products(self) -> list:
        """
        Charge les produits à partir d'un fichier JSON.
        Si le fichier n'existe pas, retourne une liste vide.
        """
        try:
            with open(self.json_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Le fichier {self.json_file} n'existe pas. Création d'une nouvelle liste.")
            return []  # Retourner une liste vide si le fichier JSON n'existe pas
        except Exception as e:
            print(f"Erreur lors du chargement des produits : {e}")
            return []

    def add_product(self, product_name:str):
        """
        Ajoute un produit à la liste et met à jour le fichier JSON.
        """
        if product_name not in self.product_names:
            self.product_names.append(product_name)
            self.save_products()
            print(f"Produit ajouté : {product_name}")
        else:
            print("Produit déjà existant ou non valide.")

    def delete_product(self, product_name: str):
        """
        Supprime un produit de la liste des produits et met à jour le fichier JSON.
        """
        if product_name in self.product_names:
            self.product_names.remove(product_name)
            self.save_products()
            print(f"Produit supprimé : {product_name}")
        else:
            print(f"Le produit '{product_name}' n'existe pas dans la liste.")


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation
    manager = ProductManager()

    # Afficher les produits chargés
    print(f"Produits chargés : {manager.product_names}")

    # Ajouter des produits
    manager.add_product("Poulets")
    manager.add_product("Dindes")
    manager.add_product("Pattes")

    # Supprimer un produit
    manager.delete_product("Dindes")  # Produit supprimé
    manager.delete_product("Poussin")  # Produit inexistant

    # Afficher la liste mise à jour
    print(f"Produits actuels : {manager.product_names}")
