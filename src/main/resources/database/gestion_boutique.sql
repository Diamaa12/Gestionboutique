PGDMP  &                    }            gestion_boutique    17.2    17.2 D               0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false                       1262    24576    gestion_boutique    DATABASE     �   CREATE DATABASE gestion_boutique WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'French_France.1252';
     DROP DATABASE gestion_boutique;
                     postgres    false            �            1255    24577    decrement_stock()    FUNCTION     �  CREATE FUNCTION public.decrement_stock() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Si un nouveau produit est vendu (INSERT)
	RAISE NOTICE '--Debut de la fonction decrement_sock()--';
	RAISE NOTICE 'Decrementation de quantite_produit de la table Produit';
    IF TG_OP = 'INSERT' THEN
        -- Décrémenter directement le stock
        UPDATE produit
        SET quantite_produit = quantite_produit - NEW.quantite_vendu
        WHERE id_produit = NEW.id_produit AND (quantite_produit >= NEW.quantite_vendu);
		RAISE NOTICE '% vient d etre soustrait au stock', NEW.quantite_vendu-(select SUM(quantite_vendu) from ventes
		where id_produit=NEW.id_produit);
		RAISE NOTICE 'Nouveau quantite_restante: %', (select stock_initial-NEW.quantite_vendu from produit
		where id_produit=NEW.id_produit);
        -- Vérifier que l'update a été effectué
        IF NOT FOUND THEN
            RAISE EXCEPTION 'L Insertion de  produit no % a échoué, Raison: stock est éupuisé', NEW.id_produit;
        END IF;

    -- Si une vente existante est modifiée (UPDATE)
    ELSIF TG_OP = 'UPDATE' THEN
        -- Calculer la différence entre la nouvelle quantité vendue et l'ancienne quantité
        UPDATE produit
        SET quantite_produit = quantite_produit - (NEW.quantite_vendu - OLD.quantite_vendu)
        WHERE id_produit = NEW.id_produit AND (quantite_produit >= (NEW.quantite_vendu - OLD.quantite_vendu));
		RAISE NOTICE '% vient d etre soustrait au stock', (NEW.quantite_vendu-OLD.quantite_vendu);
		RAISE NOTICE 'Nouveau quantite_restante: %', (select quantite_produit from produit
		where id_produit=NEW.id_produit) ;

        -- Vérification
        IF NOT FOUND THEN
            RAISE EXCEPTION 'L Update de  produit no % a échoué, Raison: stock est éupuisé', NEW.id_produit;
        END IF;
    END IF;

	RAISE NOTICE '--Fin de la fonction decrement_stock()--';
    RETURN NEW; -- Retourne les nouvelles données
	
END;
$$;
 (   DROP FUNCTION public.decrement_stock();
       public               postgres    false            �            1255    24578    reset_columns_when_stock_zero()    FUNCTION     �  CREATE FUNCTION public.reset_columns_when_stock_zero() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	RAISE NOTICE 'Debut de la fonction reset_columns_when_stock_zero'; 
    -- Vérifier si le stock devient 0 après mise à jour
    IF NEW.quantite_produit <= 0 THEN
        -- Réinitialiser la colonne ttl_somme dans la table sommes
		RAISE NOTICE 'La quantite_produit de % et %, reinitialisation de colone quantite_vendu et ttl_somme_vendu à 0',
		NEW.nom_produit, NEW.quantite_produit;
		
        UPDATE sommes
        SET ttl_somme_vendu = 0
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
$$;
 6   DROP FUNCTION public.reset_columns_when_stock_zero();
       public               postgres    false            �            1255    24579    tables_management_trigger()    FUNCTION     �  CREATE FUNCTION public.tables_management_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	RAISE NOTICE '--Debut de la fonction update_restant() de la table Restant--';
    -- Vérifier si une ligne pour ce produit existe déjà dans Restant
    IF EXISTS (SELECT 1 FROM Restant WHERE id_produit = NEW.id_produit) THEN
        -- Mettre à jour la quantité restante
        UPDATE Restant
        SET quantite_restant = (SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
                             - (SELECT SUM(quantite_vendu) FROM Ventes WHERE id_produit = NEW.id_produit),
							 date = NOW()
        WHERE id_produit = NEW.id_produit
		AND ((SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
        - (SELECT SUM(quantite_vendu) FROM Ventes WHERE id_produit = NEW.id_produit)) >= 0;
		RAISE NOTICE 'Mettre à jour la quantitté restante';
		--Le contenu de RAISE NOTICE ne sert que pour le debogage
		RAISE NOTICE 'Requete de type update.';
		RAISE NOTICE 'Pour le produit % il reste % unité.', (select nom_produit from produit where id_produit=NEW.id_produit),
		(SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
                             - (SELECT SUM(quantite_vendu) FROM Ventes WHERE id_produit = NEW.id_produit);
    ELSE
        -- Insérer une nouvelle ligne dans Restant
        INSERT INTO Restant (id_produit, quantite_restant)
        VALUES (
            NEW.id_produit,
            (SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
            - NEW.quantite_vendu
        );
		RAISE NOTICE 'Requete d insertion d une nouvelle ligne.';
		RAISE NOTICE 'Pour le produit %, il reste % untite', (select nom_produit from produit where id_produit=NEW.id_produit),
		(SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit)-NEW.quantite_vendu;
            
    END IF;
    RAISE NOTICE '--Fin de la fonction update_restant() de la Table Restant --';
	RAISE NOTICE '--FIN de la partie qui est chargé d inserer les donnés de quantite_restant dans T Restant';
	
	RAISE NOTICE '--Debut de la partie qui gere l ajout de donnes ttl_somme_vendu, ttl_somme_nn_vendu dans la table sommes ';
	    IF EXISTS (SELECT 1 FROM Sommes WHERE id_produit = NEW.id_produit) THEN
        -- Mettre à jour les totaux
        UPDATE Sommes
        SET 
            ttl_somme_vendu = (SELECT SUM(quantite_vendu * prix_vente) 
                               FROM Ventes 
                               JOIN Produit USING (id_produit)
                               WHERE id_produit = NEW.id_produit AND NEW.quantite_vendu <= (select stock_initial from produit
							   where id_produit=NEW.id_produit)),
            ttl_somme_non_vendu = (SELECT quantite_restant * prix_achat 
                                   FROM Restant 
                                   JOIN Produit USING (id_produit)
                                   WHERE id_produit = NEW.id_produit ),
			date = NOW()					   
        WHERE id_produit = NEW.id_produit AND (select quantite_restant from restant where id_produit=NEW.id_produit) >= 0;
		RAISE NOTICE 'Requete de type UPDATE.';
    ELSE
        -- Insérer une nouvelle ligne dans Sommes
        INSERT INTO Sommes (id_produit, ttl_somme_vendu, ttl_somme_non_vendu)
        VALUES (
            NEW.id_produit,
            NEW.quantite_vendu * (SELECT prix_vente FROM Produit WHERE id_produit = NEW.id_produit),
            ((SELECT quantite_produit FROM Produit WHERE id_produit = NEW.id_produit) - NEW.quantite_vendu)
            * (SELECT prix_achat FROM Produit WHERE id_produit = NEW.id_produit)
        );
		RAISE NOTICE 'Requete de type INSERT.';
    END IF;
    RAISE NOTICE '--Fin de la fonction update_sommes() de la Table Sommes--';
	RAISE NOTICE '--FIN de la partie qui gere l ajout de donnes ttl_somme_vendu, ttl_somme_nn_vendu dans la table sommes ';
	RAISE NOTICE '--Debut de la partie qui gere la decrementation de quantite_produit de la table Produit ';
	    -- Si un nouveau produit est vendu (INSERT)
		/*
	RAISE NOTICE '--Debut de la fonction decrement_sock()--';
	RAISE NOTICE 'Decrementation de quantite_produit de la table Produit';
    IF TG_OP = 'INSERT' THEN
        -- Décrémenter directement le stock
        UPDATE produit
        SET quantite_produit = quantite_produit - NEW.quantite_vendu
        WHERE id_produit = NEW.id_produit AND (quantite_produit >= NEW.quantite_vendu);
		RAISE NOTICE '% vient d etre soustrait au stock', NEW.quantite_vendu-(select SUM(quantite_vendu) from ventes
		where id_produit=NEW.id_produit);
		RAISE NOTICE 'Nouveau quantite_restante: %', (select stock_initial-NEW.quantite_vendu from produit
		where id_produit=NEW.id_produit);
        -- Vérifier que l'update a été effectué
        IF NOT FOUND THEN
            RAISE EXCEPTION 'L Insertion de  produit no % a échoué, Raison: stock est éupuisé', NEW.id_produit;
        END IF;

    -- Si une vente existante est modifiée (UPDATE)
    ELSIF TG_OP = 'UPDATE' THEN
        -- Calculer la différence entre la nouvelle quantité vendue et l'ancienne quantité
        UPDATE produit
        SET quantite_produit = quantite_produit - (NEW.quantite_vendu - OLD.quantite_vendu)
        WHERE id_produit = NEW.id_produit AND (quantite_produit >= (NEW.quantite_vendu - OLD.quantite_vendu));
		RAISE NOTICE '% vient d etre soustrait au stock', (NEW.quantite_vendu-OLD.quantite_vendu);
		RAISE NOTICE 'Nouveau quantite_restante: %', (select quantite_produit from produit
		where id_produit=NEW.id_produit) ;

        -- Vérification
        IF NOT FOUND THEN
            RAISE EXCEPTION 'L Update de  produit no % a échoué, Raison: stock est éupuisé', NEW.id_produit;
        END IF;
    END IF;

	RAISE NOTICE '--Fin de la fonction decrement_stock()--';*/
    RETURN NEW;
	
END;
$$;
 2   DROP FUNCTION public.tables_management_trigger();
       public               postgres    false            �            1255    24580    update_quantite_vendu()    FUNCTION     �  CREATE FUNCTION public.update_quantite_vendu() RETURNS trigger
    LANGUAGE plpgsql
    AS $$DECLARE
    stock_disponible INTEGER;
    total_vendu INTEGER;
BEGIN
	RAISE NOTICE '--Debut de la fonction update_quantite_vendu()--';
    -- Récupérer la quantité disponible pour le produit dans la table Produit
    SELECT stock_initial INTO stock_disponible
    FROM Produit
    WHERE id_produit = NEW.id_produit;
	RAISE NOTICE 'On a actuellement % unité dans le stock.', stock_disponible;
	RAISE NOTICE 'Quantité dèjà vendu: %', OLD.quantite_vendu;
	RAISE NOTICE 'LA quantité qui vient d etre vendu: %',(select sum(quantite_vendu) from ventes
	where id_produit=NEW.id_produit);
	RAISE NOTICE 'TOTAL Vendu: %',NEW.quantite_vendu;
	
    -- Gestion des cas INSERT et UPDATE
    IF TG_OP = 'INSERT' THEN
        -- Cas d'une insertion : total_vendu est simplement la quantité insérée
        total_vendu = NEW.quantite_vendu;

    ELSIF TG_OP = 'UPDATE' THEN
        -- Cas d'une mise à jour : total_vendu est l'ancien + le nouveau
        total_vendu = NEW.quantite_vendu;
		RAISE NOTICE '%: vient d etre vendu', total_vendu;
		RAISE NOTICE 'Il reste: % dans le stock', stock_disponible-total_vendu;

    END IF;

    -- Vérification : la nouvelle quantité totale vendue ne doit pas dépasser le stock
    IF total_vendu > stock_disponible THEN
		RAISE NOTICE 'Le Stock est vide, il n est plus possible de puise dans le stock.';
        RAISE EXCEPTION 'La quantité totale vendue (%s) dépasse le stock disponible (%s) pour le produit (ID: %s).',
        total_vendu, stock_disponible, NEW.id_produit;
    END IF;
	RAISE NOTICE '--FIN de la fonction update_quantite_vendu()--';
    RETURN NEW;
	
END;
/*
DECLARE
    stock_disponible INTEGER;
    total_vendu INTEGER;
    total_vendu_actuel INTEGER;
BEGIN
    RAISE NOTICE '--Début de la fonction update_quantite_vendu()--';

    -- Calculer le stock disponible : Stock initial - Quantité déjà vendue
    SELECT 
        stock_initial - COALESCE(SUM(quantite_vendu), 0) INTO stock_disponible
    FROM 
        Produit p
        LEFT JOIN Ventes v ON p.id_produit = v.id_produit
    WHERE 
        p.id_produit = NEW.id_produit
    GROUP BY 
        p.stock_initial;

    -- Si le stock disponible est NULL, cela signifie que le produit n'existe pas
    IF stock_disponible IS NULL THEN
        RAISE EXCEPTION 'Le produit (ID: %s) n''existe pas.', NEW.id_produit;
    END IF;

    RAISE NOTICE 'Stock disponible actuel : %', stock_disponible;

    -- Gestion des cas INSERT et UPDATE
    total_vendu_actuel = COALESCE((SELECT SUM(quantite_vendu) FROM ventes WHERE id_produit = NEW.id_produit), 0);

    IF TG_OP = 'INSERT' THEN
        -- Ajouter la quantité vendue à la somme actuelle
        total_vendu = total_vendu_actuel + NEW.quantite_vendu;

    ELSIF TG_OP = 'UPDATE' THEN
        -- Ajouter la nouvelle quantité vendue à l'ancienne
        total_vendu = total_vendu_actuel - OLD.quantite_vendu + NEW.quantite_vendu;
    END IF;

    -- Vérification : le stock ne doit pas être dépassé
    IF total_vendu > stock_disponible THEN
        RAISE NOTICE 'Le stock est insuffisant (% unités restantes).', stock_disponible;
        RAISE EXCEPTION 'La quantité totale vendue (%s) dépasse le stock disponible (%s) pour le produit (ID: %s).',
        total_vendu, stock_disponible, NEW.id_produit;
    END IF;

    RAISE NOTICE '--Fin de la fonction update_quantite_vendu()--';
    RETURN NEW;
	END;
	*/$$;
 .   DROP FUNCTION public.update_quantite_vendu();
       public               postgres    false            �            1255    24581    update_restant()    FUNCTION     �  CREATE FUNCTION public.update_restant() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	RAISE NOTICE '--Debut de la fonction update_restant() de la table Restant--';
    -- Vérifier si une ligne pour ce produit existe déjà dans Restant
    IF EXISTS (SELECT 1 FROM Restant WHERE id_produit = NEW.id_produit) THEN
        -- Mettre à jour la quantité restante
        UPDATE Restant
        SET quantite_restant = (SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
                             - (SELECT SUM(quantite_vendu) FROM Ventes WHERE id_produit = NEW.id_produit)
        WHERE id_produit = NEW.id_produit
		AND ((SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
        - (SELECT SUM(quantite_vendu) FROM Ventes WHERE id_produit = NEW.id_produit)) >= 0;
		RAISE NOTICE 'Mettre à jour la quantitße restant';
		--Le contenu de RAISE NOTICE ne sert que pour le debogage
		RAISE NOTICE 'Requete de type update.';
		RAISE NOTICE 'Pour le produit % il reste % unité.', (select nom_produit from produit where id_produit=NEW.id_produit),
		(SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
                             - (SELECT SUM(quantite_vendu) FROM Ventes WHERE id_produit = NEW.id_produit);
    ELSE
        -- Insérer une nouvelle ligne dans Restant
        INSERT INTO Restant (id_produit, quantite_restant)
        VALUES (
            NEW.id_produit,
            (SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit) 
            - NEW.quantite_vendu
        );
		RAISE NOTICE 'Requete d insertion d une nouvelle ligne.';
		RAISE NOTICE 'Pour le produit %, il reste % untite', (select nom_produit from produit where id_produit=NEW.id_produit),
		(SELECT stock_initial FROM Produit WHERE id_produit = NEW.id_produit)-NEW.quantite_vendu;
            
    END IF;
    RAISE NOTICE '--Fin de la fonction update_restant() de la Table Restant --';
    RETURN NEW;
	
END;
$$;
 '   DROP FUNCTION public.update_restant();
       public               postgres    false            �            1255    24582    update_sommes()    FUNCTION     �  CREATE FUNCTION public.update_sommes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$DECLARE quantite_produit_actuel INTEGER;
BEGIN
    -- Vérifier si une ligne existe déjà dans Sommes
	RAISE NOTICE '--Debut de la fonction update_sommes() de la Table Sommes--';
	--on recupere la valeur de quantite_produit
	/*SELECT quantite_produit into quantite_produit_actuel
	FROM produit WHERE id_produit=NEW.id_produit;
	 -- Vérifier si la quantité du produit est positive
    IF quantite_produit_actuel > 0 THEN
        -- Si la quantité est positive, continuez normalement
        RETURN NEW;
    ELSE
        UPDATE Ventes
		SET quantite_vendu = 0
		WHERE id_produit=NEW.id_produit;
    END IF;*/

	
    IF EXISTS (SELECT 1 FROM Sommes WHERE id_produit = NEW.id_produit) THEN
        -- Mettre à jour les totaux
        UPDATE Sommes
        SET 
            ttl_somme_vendu = (SELECT SUM(quantite_vendu * prix_vente) 
                               FROM Ventes 
                               JOIN Produit USING (id_produit)
                               WHERE id_produit = NEW.id_produit AND NEW.quantite_vendu <= (select stock_initial from produit
							   where id_produit=NEW.id_produit)),
            ttl_somme_non_vendu = (SELECT quantite_restant * prix_achat 
                                   FROM Restant 
                                   JOIN Produit USING (id_produit)
                                   WHERE id_produit = NEW.id_produit )
        WHERE id_produit = NEW.id_produit AND quantite_restant >= 0;
		RAISE NOTICE 'Requete de type UPDATE.';
    ELSE
        -- Insérer une nouvelle ligne dans Sommes
        INSERT INTO Sommes (id_produit, ttl_somme_vendu, ttl_somme_non_vendu)
        VALUES (
            NEW.id_produit,
            NEW.quantite_vendu * (SELECT prix_vente FROM Produit WHERE id_produit = NEW.id_produit),
            ((SELECT quantite_produit FROM Produit WHERE id_produit = NEW.id_produit) - NEW.quantite_vendu)
            * (SELECT prix_achat FROM Produit WHERE id_produit = NEW.id_produit)
        );
		RAISE NOTICE 'Requete de type INSERT.';
    END IF;
    RAISE NOTICE '--Fin de la fonction update_sommes() de la Table Sommes--';
    RETURN NEW;
	
END;
$$;
 &   DROP FUNCTION public.update_sommes();
       public               postgres    false            �            1255    24583 !   update_sommes_on_produit_change()    FUNCTION     [  CREATE FUNCTION public.update_sommes_on_produit_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
RAISE NOTICE '--Debut de la fonction update_sommes_on_produit_change() de la Table Sommes--';
    -- Mettre à jour les totaux de la table Sommes en cas de changement de prix dans la table produit--
	--si un produit augmente il faut recalculer son prix et mettre á jour la table sommes--
	--Raison pour laquelle on utilise ici OLD.id_produit--
    UPDATE Sommes
    SET 
        ttl_somme_vendu = (SELECT SUM(quantite_vendu * prix_vente) 
                           FROM Ventes 
                           JOIN Produit USING (id_produit)
                           WHERE id_produit = OLD.id_produit),
        ttl_somme_non_vendu = (SELECT quantite_restant * prix_achat 
                               FROM Restant 
                               JOIN Produit USING (id_produit)
                               WHERE id_produit = OLD.id_produit)
    WHERE id_produit = OLD.id_produit;

	RAISE NOTICE '--Fin de la fonction update_sommes_on_produit_change() de la Table Sommes--';

    RETURN NEW;
	END;
$$;
 8   DROP FUNCTION public.update_sommes_on_produit_change();
       public               postgres    false            �            1259    24584    historique_product_quantite    TABLE     �   CREATE TABLE public.historique_product_quantite (
    id integer NOT NULL,
    id_produit integer NOT NULL,
    historique_quantite integer NOT NULL,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 /   DROP TABLE public.historique_product_quantite;
       public         heap r       postgres    false            �            1259    24588 "   historique_product_quantite_id_seq    SEQUENCE     �   CREATE SEQUENCE public.historique_product_quantite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.historique_product_quantite_id_seq;
       public               postgres    false    217                       0    0 "   historique_product_quantite_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.historique_product_quantite_id_seq OWNED BY public.historique_product_quantite.id;
          public               postgres    false    218            �            1259    24589    historique_ventes    TABLE     �   CREATE TABLE public.historique_ventes (
    id integer NOT NULL,
    id_produit integer NOT NULL,
    quantite numeric NOT NULL,
    date_vente timestamp without time zone NOT NULL
);
 %   DROP TABLE public.historique_ventes;
       public         heap r       postgres    false            �            1259    24594    historique_ventes_id_seq    SEQUENCE     �   CREATE SEQUENCE public.historique_ventes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.historique_ventes_id_seq;
       public               postgres    false    219                       0    0    historique_ventes_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.historique_ventes_id_seq OWNED BY public.historique_ventes.id;
          public               postgres    false    220            �            1259    24595    produit    TABLE     R  CREATE TABLE public.produit (
    id_produit integer NOT NULL,
    nom_produit character varying(255),
    quantite_produit integer NOT NULL,
    prix_achat numeric(10,2) NOT NULL,
    prix_vente numeric(10,2) NOT NULL,
    date_achat timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    stock_initial integer DEFAULT 0 NOT NULL
);
    DROP TABLE public.produit;
       public         heap r       postgres    false            �            1259    24600    produit_id_produit_seq    SEQUENCE     �   CREATE SEQUENCE public.produit_id_produit_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.produit_id_produit_seq;
       public               postgres    false    221                       0    0    produit_id_produit_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.produit_id_produit_seq OWNED BY public.produit.id_produit;
          public               postgres    false    222            �            1259    24601    restant    TABLE     �   CREATE TABLE public.restant (
    id_restant integer NOT NULL,
    id_produit integer NOT NULL,
    quantite_restant integer DEFAULT 0,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.restant;
       public         heap r       postgres    false            �            1259    24606    restant_id_restant_seq    SEQUENCE     �   CREATE SEQUENCE public.restant_id_restant_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.restant_id_restant_seq;
       public               postgres    false    223                       0    0    restant_id_restant_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.restant_id_restant_seq OWNED BY public.restant.id_restant;
          public               postgres    false    224            �            1259    24607    sommes    TABLE     �   CREATE TABLE public.sommes (
    id_somme integer NOT NULL,
    id_produit integer NOT NULL,
    ttl_somme_vendu numeric(10,2) DEFAULT 0,
    ttl_somme_non_vendu numeric(10,2) DEFAULT 0,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.sommes;
       public         heap r       postgres    false            �            1259    24613    sommes_id_somme_seq    SEQUENCE     �   CREATE SEQUENCE public.sommes_id_somme_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.sommes_id_somme_seq;
       public               postgres    false    225                       0    0    sommes_id_somme_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.sommes_id_somme_seq OWNED BY public.sommes.id_somme;
          public               postgres    false    226            �            1259    24614    stock_disponible    TABLE     @   CREATE TABLE public.stock_disponible (
    "?column?" bigint
);
 $   DROP TABLE public.stock_disponible;
       public         heap r       postgres    false            �            1259    24617    ventes    TABLE     �   CREATE TABLE public.ventes (
    id_ventes integer NOT NULL,
    id_produit integer NOT NULL,
    quantite_vendu integer DEFAULT 0 NOT NULL,
    date_vente timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.ventes;
       public         heap r       postgres    false            �            1259    24622    ventes_id_ventes_seq    SEQUENCE     �   CREATE SEQUENCE public.ventes_id_ventes_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.ventes_id_ventes_seq;
       public               postgres    false    228                       0    0    ventes_id_ventes_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.ventes_id_ventes_seq OWNED BY public.ventes.id_ventes;
          public               postgres    false    229            E           2604    24623    historique_product_quantite id    DEFAULT     �   ALTER TABLE ONLY public.historique_product_quantite ALTER COLUMN id SET DEFAULT nextval('public.historique_product_quantite_id_seq'::regclass);
 M   ALTER TABLE public.historique_product_quantite ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    218    217            G           2604    24624    historique_ventes id    DEFAULT     |   ALTER TABLE ONLY public.historique_ventes ALTER COLUMN id SET DEFAULT nextval('public.historique_ventes_id_seq'::regclass);
 C   ALTER TABLE public.historique_ventes ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    220    219            H           2604    24625    produit id_produit    DEFAULT     x   ALTER TABLE ONLY public.produit ALTER COLUMN id_produit SET DEFAULT nextval('public.produit_id_produit_seq'::regclass);
 A   ALTER TABLE public.produit ALTER COLUMN id_produit DROP DEFAULT;
       public               postgres    false    222    221            K           2604    24626    restant id_restant    DEFAULT     x   ALTER TABLE ONLY public.restant ALTER COLUMN id_restant SET DEFAULT nextval('public.restant_id_restant_seq'::regclass);
 A   ALTER TABLE public.restant ALTER COLUMN id_restant DROP DEFAULT;
       public               postgres    false    224    223            N           2604    24627    sommes id_somme    DEFAULT     r   ALTER TABLE ONLY public.sommes ALTER COLUMN id_somme SET DEFAULT nextval('public.sommes_id_somme_seq'::regclass);
 >   ALTER TABLE public.sommes ALTER COLUMN id_somme DROP DEFAULT;
       public               postgres    false    226    225            R           2604    24628    ventes id_ventes    DEFAULT     t   ALTER TABLE ONLY public.ventes ALTER COLUMN id_ventes SET DEFAULT nextval('public.ventes_id_ventes_seq'::regclass);
 ?   ALTER TABLE public.ventes ALTER COLUMN id_ventes DROP DEFAULT;
       public               postgres    false    229    228                       0    24584    historique_product_quantite 
   TABLE DATA           `   COPY public.historique_product_quantite (id, id_produit, historique_quantite, date) FROM stdin;
    public               postgres    false    217   �                 0    24589    historique_ventes 
   TABLE DATA           Q   COPY public.historique_ventes (id, id_produit, quantite, date_vente) FROM stdin;
    public               postgres    false    219   ��                 0    24595    produit 
   TABLE DATA              COPY public.produit (id_produit, nom_produit, quantite_produit, prix_achat, prix_vente, date_achat, stock_initial) FROM stdin;
    public               postgres    false    221   }�                 0    24601    restant 
   TABLE DATA           Q   COPY public.restant (id_restant, id_produit, quantite_restant, date) FROM stdin;
    public               postgres    false    223   X�                 0    24607    sommes 
   TABLE DATA           b   COPY public.sommes (id_somme, id_produit, ttl_somme_vendu, ttl_somme_non_vendu, date) FROM stdin;
    public               postgres    false    225   �       
          0    24614    stock_disponible 
   TABLE DATA           6   COPY public.stock_disponible ("?column?") FROM stdin;
    public               postgres    false    227   ��                 0    24617    ventes 
   TABLE DATA           S   COPY public.ventes (id_ventes, id_produit, quantite_vendu, date_vente) FROM stdin;
    public               postgres    false    228   ��                  0    0 "   historique_product_quantite_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.historique_product_quantite_id_seq', 18, true);
          public               postgres    false    218                       0    0    historique_ventes_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.historique_ventes_id_seq', 40, true);
          public               postgres    false    220                       0    0    produit_id_produit_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.produit_id_produit_seq', 28, true);
          public               postgres    false    222                       0    0    restant_id_restant_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.restant_id_restant_seq', 9, true);
          public               postgres    false    224                       0    0    sommes_id_somme_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.sommes_id_somme_seq', 9, true);
          public               postgres    false    226                       0    0    ventes_id_ventes_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.ventes_id_ventes_seq', 9, true);
          public               postgres    false    229            V           2606    24630 <   historique_product_quantite historique_product_quantite_pkey 
   CONSTRAINT     z   ALTER TABLE ONLY public.historique_product_quantite
    ADD CONSTRAINT historique_product_quantite_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.historique_product_quantite DROP CONSTRAINT historique_product_quantite_pkey;
       public                 postgres    false    217            X           2606    24632 (   historique_ventes historique_ventes_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.historique_ventes
    ADD CONSTRAINT historique_ventes_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.historique_ventes DROP CONSTRAINT historique_ventes_pkey;
       public                 postgres    false    219            Z           2606    24634    produit nom_produit_unique 
   CONSTRAINT     \   ALTER TABLE ONLY public.produit
    ADD CONSTRAINT nom_produit_unique UNIQUE (nom_produit);
 D   ALTER TABLE ONLY public.produit DROP CONSTRAINT nom_produit_unique;
       public                 postgres    false    221            \           2606    24636    produit produit_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.produit
    ADD CONSTRAINT produit_pkey PRIMARY KEY (id_produit);
 >   ALTER TABLE ONLY public.produit DROP CONSTRAINT produit_pkey;
       public                 postgres    false    221            ^           2606    24638    restant restant_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.restant
    ADD CONSTRAINT restant_pkey PRIMARY KEY (id_restant);
 >   ALTER TABLE ONLY public.restant DROP CONSTRAINT restant_pkey;
       public                 postgres    false    223            `           2606    24640    sommes sommes_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.sommes
    ADD CONSTRAINT sommes_pkey PRIMARY KEY (id_somme);
 <   ALTER TABLE ONLY public.sommes DROP CONSTRAINT sommes_pkey;
       public                 postgres    false    225            b           2606    24642    ventes ventes_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.ventes
    ADD CONSTRAINT ventes_pkey PRIMARY KEY (id_ventes);
 <   ALTER TABLE ONLY public.ventes DROP CONSTRAINT ventes_pkey;
       public                 postgres    false    228            j           2620    24643 !   ventes talbes_management_triggers    TRIGGER     �   CREATE TRIGGER talbes_management_triggers AFTER INSERT OR UPDATE ON public.ventes FOR EACH ROW EXECUTE FUNCTION public.tables_management_trigger();
 :   DROP TRIGGER talbes_management_triggers ON public.ventes;
       public               postgres    false    244    228            k           2620    24644    ventes trigger_decrement_stock    TRIGGER     �   CREATE TRIGGER trigger_decrement_stock AFTER INSERT OR UPDATE ON public.ventes FOR EACH ROW EXECUTE FUNCTION public.decrement_stock();

ALTER TABLE public.ventes DISABLE TRIGGER trigger_decrement_stock;
 7   DROP TRIGGER trigger_decrement_stock ON public.ventes;
       public               postgres    false    230    228            h           2620    24645 #   produit trigger_reset_on_stock_zero    TRIGGER     �   CREATE TRIGGER trigger_reset_on_stock_zero AFTER UPDATE OF quantite_produit ON public.produit FOR EACH ROW EXECUTE FUNCTION public.reset_columns_when_stock_zero();

ALTER TABLE public.produit DISABLE TRIGGER trigger_reset_on_stock_zero;
 <   DROP TRIGGER trigger_reset_on_stock_zero ON public.produit;
       public               postgres    false    231    221    221            l           2620    24646    ventes trigger_update_restant    TRIGGER     �   CREATE TRIGGER trigger_update_restant AFTER INSERT OR UPDATE ON public.ventes FOR EACH ROW EXECUTE FUNCTION public.update_restant();

ALTER TABLE public.ventes DISABLE TRIGGER trigger_update_restant;
 6   DROP TRIGGER trigger_update_restant ON public.ventes;
       public               postgres    false    246    228            m           2620    24647    ventes trigger_update_sommes    TRIGGER     �   CREATE TRIGGER trigger_update_sommes AFTER INSERT OR UPDATE ON public.ventes FOR EACH ROW EXECUTE FUNCTION public.update_sommes();

ALTER TABLE public.ventes DISABLE TRIGGER trigger_update_sommes;
 5   DROP TRIGGER trigger_update_sommes ON public.ventes;
       public               postgres    false    247    228            i           2620    24648 (   produit trigger_update_sommes_on_produit    TRIGGER     �   CREATE TRIGGER trigger_update_sommes_on_produit AFTER UPDATE ON public.produit FOR EACH ROW EXECUTE FUNCTION public.update_sommes_on_produit_change();

ALTER TABLE public.produit DISABLE TRIGGER trigger_update_sommes_on_produit;
 A   DROP TRIGGER trigger_update_sommes_on_produit ON public.produit;
       public               postgres    false    232    221            n           2620    24649    ventes update_quantite_vendu    TRIGGER     �   CREATE TRIGGER update_quantite_vendu BEFORE INSERT OR UPDATE ON public.ventes FOR EACH ROW EXECUTE FUNCTION public.update_quantite_vendu();
 5   DROP TRIGGER update_quantite_vendu ON public.ventes;
       public               postgres    false    245    228            d           2606    24650    historique_ventes fk_produit    FK CONSTRAINT     �   ALTER TABLE ONLY public.historique_ventes
    ADD CONSTRAINT fk_produit FOREIGN KEY (id_produit) REFERENCES public.produit(id_produit) ON DELETE CASCADE;
 F   ALTER TABLE ONLY public.historique_ventes DROP CONSTRAINT fk_produit;
       public               postgres    false    4700    219    221            c           2606    24655 &   historique_product_quantite fk_produit    FK CONSTRAINT     �   ALTER TABLE ONLY public.historique_product_quantite
    ADD CONSTRAINT fk_produit FOREIGN KEY (id_produit) REFERENCES public.produit(id_produit) ON DELETE CASCADE;
 P   ALTER TABLE ONLY public.historique_product_quantite DROP CONSTRAINT fk_produit;
       public               postgres    false    221    4700    217            e           2606    24660    restant restant_id_produit_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.restant
    ADD CONSTRAINT restant_id_produit_fkey FOREIGN KEY (id_produit) REFERENCES public.produit(id_produit) ON DELETE CASCADE;
 I   ALTER TABLE ONLY public.restant DROP CONSTRAINT restant_id_produit_fkey;
       public               postgres    false    223    4700    221            f           2606    24665    sommes sommes_id_produit_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.sommes
    ADD CONSTRAINT sommes_id_produit_fkey FOREIGN KEY (id_produit) REFERENCES public.produit(id_produit) ON DELETE CASCADE;
 G   ALTER TABLE ONLY public.sommes DROP CONSTRAINT sommes_id_produit_fkey;
       public               postgres    false    221    225    4700            g           2606    24670    ventes ventes_id_produit_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.ventes
    ADD CONSTRAINT ventes_id_produit_fkey FOREIGN KEY (id_produit) REFERENCES public.produit(id_produit) ON DELETE CASCADE;
 G   ALTER TABLE ONLY public.ventes DROP CONSTRAINT ventes_id_produit_fkey;
       public               postgres    false    228    221    4700                �   x�e���0�bn���H���_Gd��9���P�abq����H�XJ�0��Ft�CWQ\�x!� #%��5���٘\Z�����CV����s�3���jI^s'ͭy08�wm{r�̩���������1V8����3$         �  x�m�ˍ�0D�f����R,�[rc�m{ ��\�")�a��?,?/�s��3-H9���\�ó�hn�sX�w���O�d���u���`��I�+�6а��A�+�	������ ��b^8ࠉ�|i��H!���
�}FKOn����El=��Iv/�N�b���H�\?���~G��plH�:l�z��)L�XIA�	��`�TI
6���/mE;��!zG�Zb�c�Ac^��M#��*/'e��N`9b��q��4��v��s+n3h�e߄�1��2�O��0���΅��3ɍ����V#�?4�-g���kOMv�|�gP�W�v*�wLq^�y)+w�S"��mT�J�c�c�/�^�����XT�����V��*d�ꋀ�Nf<����D<�_�J }��G{̔�I6���y�Q-�1����D>�a��"����R         �   x�m�Mj1���)|���'��B�tSh!Yxz�z&mIBA����I����5�rRL2 ��w�v gyX��S�T1���>��<$��CF{ �A�;K�9DU�����r^':wQ}��';kG	���$��Lޖ�&my��.œ�̓���b��Q���s���Hڳ3yj��u�dN�?Mr��L�ߤ��x�fk��ރs�)�D�         |   x�e��	1DѳT�X#�Hv�Z��BH�9>���x-�!/�5�h˹�U����GІ�Y��A��R(H{\�4��6W<�Ob�EG�y���H�>�cV�B�/�7�n������T��6%�         �   x�u���@�P�5�Ӳ���Z��e;REⱏ))@�v\�`n�����\�>��tHI��2K~�_^+��3�����g� ����\�3a�	S�}��q�#Fn,�P��#�$��8��!!N<���2O��u�qd��U��S5�      
      x�3��52�24�0��54����� "n�         z   x�e���0��4��!��i��?G�h��`H��0?P�Ё����Ҕ���ӆ�Y��X^J�8�KpЈg­������+g�Q
��� �Y��9kẞ��/��n���=��T��e$y     