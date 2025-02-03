import os
from pathlib import Path
JSON_FILES = os.path.join(Path.cwd(), ".JSON_FILES")

# On recupere les deux fichiers json
PATH_PRODUCT_NAME = Path(__file__).parent.parent.parent.absolute() / 'noms_produits.json'
PATH_BOYED_PRODUCT = Path(__file__).parent.parent.parent.absolute() / 'quantite_vendu.json'
PATH_NO_BOYED_PRODUCT = Path(__file__).parent.parent.parent.absolute() / 'quantite_restante.json'

PATH_BUYED_PRICE_PER_UNITE = Path(__file__).resolve().parent.parent.parent / 'prix_dachat_unite.json'
PATH_CELL_PRICE_PER_UNITE = Path(__file__).resolve().parent.parent.parent / 'prix_de_vente_unite.json'
PATH_TTL_SOMME_FOR_ANY_UNITE = Path(__file__).resolve().parent.parent.parent / 'ttl_prix_pour_chaque_produit.json'

PATH_TTL_SOMME_NOT_CELLED_PRODUCT_FOR_ANY_ITEM = Path(__file__).resolve().parent.parent.parent / 'ttl_prix_non_vendu_chaque_produit.json'

PATH_PRODUIT_DISPO_OR_FINISH = Path(__file__).resolve().parent.parent.parent / 'produits_dispo.json'

PATH_TTL_SOMME_FOR_ALL_CELLED_PRODUCT = Path(__file__).parent.parent.parent.absolute() / 'ttl_sommes_vendu_de_tout_les_produits.json'