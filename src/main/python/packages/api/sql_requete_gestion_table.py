creationtable = """-- Table Produit
    CREATE TABLE Produit (
        id_produit SERIAL PRIMARY KEY,
        quantite_produit INT NOT NULL,
        prix_achat DECIMAL(10, 2) NOT NULL,
        prix_vente DECIMAL(10, 2) NOT NULL
    );
    
    -- Table Ventes
    CREATE TABLE Ventes (
        id_ventes SERIAL PRIMARY KEY,
        id_produit INT NOT NULL,
        quantite_vendu INT NOT NULL,
        FOREIGN KEY (id_produit) REFERENCES Produit(id_produit)
    );
    
    -- Table Restant
    CREATE TABLE Restant (
        id_restant SERIAL PRIMARY KEY,
        id_produit INT NOT NULL,
        quantite_restant INT DEFAULT 0,
        FOREIGN KEY (id_produit) REFERENCES Produit(id_produit)
    );
    
    -- Table Sommes
    CREATE TABLE Sommes (
        id_somme SERIAL PRIMARY KEY,
        id_produit INT NOT NULL,
        ttl_somme_vendu DECIMAL(10, 2) DEFAULT 0,
        ttl_somme_non_vendu DECIMAL(10, 2) DEFAULT 0,
        FOREIGN KEY (id_produit) REFERENCES Produit(id_produit)
    );"""


'''Ce trigger sera déclenché après une **insertion ou une mise à jour** sur la table `Ventes`. Il met à jour/insère les données dans Restant'''

trigger_de_mis_a_jour1 = """CREATE OR REPLACE FUNCTION update_restant()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier si une ligne pour ce produit existe déjà dans Restant
    IF EXISTS (SELECT 1 FROM Restant WHERE id_produit = NEW.id_produit) THEN
        -- Mettre à jour la quantité restante
        UPDATE Restant
        SET quantite_restant = (SELECT quantite_produit FROM Produit WHERE id_produit = NEW.id_produit) 
                             - (SELECT SUM(quantite_vendu) FROM Ventes WHERE id_produit = NEW.id_produit)
        WHERE id_produit = NEW.id_produit;
    ELSE
        -- Insérer une nouvelle ligne dans Restant
        INSERT INTO Restant (id_produit, quantite_restant)
        VALUES (
            NEW.id_produit,
            (SELECT quantite_produit FROM Produit WHERE id_produit = NEW.id_produit) 
            - NEW.quantite_vendu
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du trigger pour `quantite_restant`
CREATE TRIGGER trigger_update_restant
AFTER INSERT OR UPDATE ON Ventes
FOR EACH ROW EXECUTE FUNCTION update_restant();"""

'''##### 
Ce trigger gère automatiquement les colonnes `ttl_somme_vendu` et `ttl_somme_non_vendu` dans la table `Sommes`.'''

trigger_de_mis_a_jour2 = """
CREATE OR REPLACE FUNCTION update_sommes()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier si une ligne existe déjà dans Sommes
    IF EXISTS (SELECT 1 FROM Sommes WHERE id_produit = NEW.id_produit) THEN
        -- Mettre à jour les totaux
        UPDATE Sommes
        SET 
            ttl_somme_vendu = (SELECT SUM(quantite_vendu * prix_vente) 
                               FROM Ventes 
                               JOIN Produit USING (id_produit)
                               WHERE id_produit = NEW.id_produit),
            ttl_somme_non_vendu = (SELECT quantite_restant * prix_achat 
                                   FROM Restant 
                                   JOIN Produit USING (id_produit)
                                   WHERE id_produit = NEW.id_produit)
        WHERE id_produit = NEW.id_produit;
    ELSE
        -- Insérer une nouvelle ligne dans Sommes
        INSERT INTO Sommes (id_produit, ttl_somme_vendu, ttl_somme_non_vendu)
        VALUES (
            NEW.id_produit,
            NEW.quantite_vendu * (SELECT prix_vente FROM Produit WHERE id_produit = NEW.id_produit),
            ((SELECT quantite_produit FROM Produit WHERE id_produit = NEW.id_produit) - NEW.quantite_vendu)
            * (SELECT prix_achat FROM Produit WHERE id_produit = NEW.id_produit)
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du trigger pour `Sommes`
CREATE TRIGGER trigger_update_sommes
AFTER INSERT OR UPDATE ON Ventes
FOR EACH ROW EXECUTE FUNCTION update_sommes();
"""

'''##### 
Si le prix d'achat ou de vente change dans la table `Produit`, les données de `Sommes` doivent également être recalculées.'''

trigger_de_mise_a_jour3 = """
##### 
Si le prix d'achat ou de vente change dans la table `Produit`, les données de `Sommes` doivent également être recalculées.
"""
'''#### 
Ajoutez un **trigger** à la table `Ventes` qui vérifie si une vente est autorisée avant de procéder à l'insertion des données. Si la quantité vendue dépasse le stock disponible (quantité dans `Produit`), la transaction sera bloquée.'''
trigger_de_mis_a_jour4 = """
CREATE OR REPLACE FUNCTION update_quantite_vendu()
RETURNS TRIGGER AS $$
DECLARE
    stock_disponible INTEGER;
    total_vendu INTEGER;
BEGIN
    -- Récupérer la quantité disponible pour le produit dans la table Produit
    SELECT quantite_produit INTO stock_disponible
    FROM Produit
    WHERE id_produit = NEW.id_produit;

    -- Calculer la nouvelle quantité totale vendue
    total_vendu = OLD.quantite_vendu + NEW.quantite_vendu;

    -- Vérification : la nouvelle quantité totale vendue ne doit pas dépasser le stock
    IF total_vendu > stock_disponible THEN
        RAISE EXCEPTION 'La quantité totale vendue (%s) dépasse le stock disponible (%s) pour le produit (ID: %s).',
        total_vendu, stock_disponible, NEW.id_produit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_quantite_vendu
BEFORE INSERT OR UPDATE ON ventes
FOR EACH ROW
EXECUTE FUNCTION update_quantite_vendu();
"""
decrement_produit = """
-- 1. Créer ou remplacer la fonction de déclenchement
CREATE OR REPLACE FUNCTION update_or_decrement_stock()
RETURNS TRIGGER AS $$
BEGIN
    -- Si un nouveau produit est vendu (INSERT)
    IF TG_OP = 'INSERT' THEN
        -- Décrémenter directement le stock
        UPDATE produit
        SET quantite_produit = quantite_produit - NEW.quantite_vendu
        WHERE id_produit = NEW.id_produit;

        -- Vérifier que l'update a été effectué
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Produit avec id_produit % introuvable dans la table produit.', NEW.id_produit;
        END IF;

    -- Si une vente existante est modifiée (UPDATE)
    ELSIF TG_OP = 'UPDATE' THEN
        -- Calculer la différence entre la nouvelle quantité vendue et l'ancienne quantité
        UPDATE produit
        SET quantite_produit = quantite_produit - (NEW.quantite_vendu - OLD.quantite_vendu)
        WHERE id_produit = NEW.id_produit;

        -- Vérification
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Produit avec id_produit % introuvable dans la table produit.', NEW.id_produit;
        END IF;
    END IF;

    RETURN NEW; -- Retourne les nouvelles données
END;
$$ LANGUAGE plpgsql;

-- 2. Appliquer le trigger sur INSERT ou UPDATE dans la table ventes
DROP TRIGGER IF EXISTS trigger_update_stock ON ventes; -- Si un trigger existait déjà
CREATE TRIGGER trigger_update_stock
AFTER INSERT OR UPDATE ON ventes
FOR EACH ROW
EXECUTE FUNCTION update_or_decrement_stock();
"""
reinitialiser_quantite_vendu_et_ttl_somme_vendu_a_zero = """
select * from produit;
CREATE OR REPLACE FUNCTION reset_columns_when_stock_zero()
RETURNS TRIGGER AS $$
BEGIN
	RAISE NOTICE 'Debut de la fonction reset_columns_when_stock_zero'; 
    -- Vérifier si le stock devient 0 après mise à jour
    IF NEW.quantite_produit = 0 THEN
        -- Réinitialiser la colonne ttl_somme dans la table sommes
		RAISE NOTICE 'La quantite_produit de % et %, reinitialisation de colone quantite_vendu et ttl_somme_vendu à 0',
		NEW.nom_produit, NEW.quantite_produit;
		
        UPDATE sommes
        SET ttl_somme = 0
        WHERE id_produit = NEW.id_produit;

        -- Réinitialiser la colonne quantite_vendu dans la table ventes
        UPDATE ventes
        SET quantite_vendu = 0
        WHERE id_produit = NEW.id_produit;
    END IF;

    -- Continuer l'opération normale
	RAISE NOTICE 'Fin de la fonction reset_columns_when_stock_zero'; 
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trigger_reset_on_stock_zero
AFTER UPDATE OF quantite_produit ON produit
FOR EACH ROW
EXECUTE FUNCTION reset_columns_when_stock_zero();
"""