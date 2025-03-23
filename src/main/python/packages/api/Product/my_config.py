import json
import logging
import os
import subprocess
from pathlib import Path
import psycopg2
import platform

from dotenv import load_dotenv

from .gestion_logger import setup_logger_with_rotation
from .resource_factory import RessourceFactory

# Définir les paramètres de connexion PostgreSQL

# Configuration
BACKUP_FILE = r"C:\ProgramData\MyDBBackup\gestion_boutique.dump" if platform.system() == "Windows" else "/var/lib/myapp/mydatabase.dump"

env_path = Path(__file__).parent.parent.parent.parent.parent.absolute() / 'resources/base/.data_base_login'
print('Chemin vers fichiers .env', env_path)
load_dotenv(dotenv_path=env_path)  # Charge les variables du .env dans les variables d'environnement


PG_ADMIN_USER = os.getenv("PG_ADMIN_USER")
PG_ADMIN_PASSWORD = os.getenv("PG_ADMIN_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
DB_NAME = os.getenv("DB_NAME")
#Copier le mot de passe de l'utilisateur postgres dans un variable dn'environnment
postgres_pass_env = os.environ.copy()
postgres_pass_env['PGPASSWORD'] = PG_ADMIN_PASSWORD
#Initialisation du fichier de configuration du logger
logguer = setup_logger_with_rotation('APPConfig', 'app_config.log')
logguer.info("Lancement du fichier de configuration.")
def initialiser_config():
    """Initialiser la configuration de l'application."""
    # Obtenir le dossier Documents de l'utilisateur courant
    dossier_documents = Path(os.getenv("PROGRAMDATA")) / "BBLTech/PRODUCT_JSON"  # Vous pouvez changer 'MonApplication' selon vos besoins
    dossier_documents.mkdir(parents=True, exist_ok=True)  # Créer le dossier si nécessaire
    print(f"Répertoire de configuration : {dossier_documents}")

    # Chemin du fichier JSON
    fichier_json = dossier_documents / 'products.json'
    print(f"Chemin du fichier JSON : {fichier_json}")

    # Vérifier si le fichier JSON existe, sinon le créer avec des données par défaut
    if not fichier_json.exists():
        try:
            print(f"Création du fichier JSON dans {fichier_json}")
            donnees_par_defaut = ['']
            with fichier_json.open(mode='w', encoding='utf-8') as fichier:
                json.dump(donnees_par_defaut, fichier, indent=4, ensure_ascii=False)
            logguer.info(f"Fichier {fichier_json} a été crée avec succées.")
        except Exception as e:
            print(f"Erreur lors de la création du fichier JSON : {e}")
            logguer.error(f"Une erreur a eu lieu lors de création du fichier JSON: {e}")
    else:
        print("Le fichier JSON existe déjà, aucune création nécessaire.")
        logguer.info('Le fichier JSON existe déjà.')
    logguer.info("--" * 20)
#Creation de la base de donnés si elle n'existe pas


#Verifier si PostgreSQL est dèjà installé
def is_postgresql_installed_and_setup():
    """
    Vérifie si PostgreSQL est installé et crée un utilisateur admin si nécessaire (Windows & Linux/macOS).
    """
    try:
        # Vérifier si PostgreSQL est installé
        #cette ligne a besoin que Postgresql soit dèjá ajouter au path system dans le cas de windows
        #sinon cette ligne ne s'executera pas
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True, check=True)
        print(f"PostgreSQL est installé : {result.stdout.strip()}")

        # Détection de l'OS
        system_platform = platform.system()
        if system_platform == "Windows":
            logguer.info("Parametrage de l'utilisateur PostgreSQL sous Windows")
            # Vérifier si l'utilisateur existe sous Windows
            print("Vous etes sous windows.")
            check_user_cmd = f'psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'{PG_ADMIN_USER}\'"'
            print(check_user_cmd)
            user_exists = subprocess.run(check_user_cmd, shell=True, capture_output=True, text=True, env=postgres_pass_env).stdout.strip()
            print(user_exists)
            print(type(user_exists))
            if user_exists != "1":
                create_user_cmd = f'psql -U postgres -c "CREATE ROLE {PG_ADMIN_USER} WITH LOGIN SUPERUSER PASSWORD \'{PG_ADMIN_PASSWORD}\';"'
                subprocess.run(create_user_cmd, shell=True, check=True, env=postgres_pass_env)
                logguer.info(f"L'utilsateur PostgreSQL {PG_ADMIN_USER} a été crée avec succés sous Windows.")
                print(f"Utilisateur PostgreSQL '{PG_ADMIN_USER}' créé avec succès sous Windows.")
            else:
                print(f"L'utilisateur PostgreSQL '{PG_ADMIN_USER}' existe déjà sous Windows.")
                logguer.info(f"L'utilisateur PostgreSQL '{PG_ADMIN_USER}' existe déjà sous Windows.")

        else:  # Linux/macOS
            logguer.info("Parametrage de l'utilisateur PostgreSQL sous Linux/macOS")
            check_user_cmd = f"sudo -u postgres psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='{PG_ADMIN_USER}'\""
            user_exists = subprocess.run(check_user_cmd, shell=True, capture_output=True, text=True).stdout.strip()

            if user_exists != "1":
                create_user_cmd = f"sudo -u postgres psql -c \"CREATE ROLE {PG_ADMIN_USER} WITH LOGIN SUPERUSER PASSWORD '{PG_ADMIN_PASSWORD}';\""
                subprocess.run(create_user_cmd, shell=True, check=True)
                print(f"Utilisateur PostgreSQL '{PG_ADMIN_USER}' créé avec succès sous Linux/macOS.")
                logguer.info(f"Utilisateur PostgreSQL '{PG_ADMIN_USER}' créé avec succès sous Linux/macOS.")
            else:
                print(f"L'utilisateur PostgreSQL '{PG_ADMIN_USER}' existe déjà sous Linux/macOS.")
                logguer.info(f"L'utilisateur PostgreSQL '{PG_ADMIN_USER}' existe déjà sous Linux/macOS.")
        logguer.info("--" * 20)
        return True
    except FileNotFoundError as e:
        print("Erreur : PostgreSQL n'est pas installé sur cette machine.")
        logguer.error(f"Erreur: {e}; PostgreSQL n'est pas installé sur cette machine.")
        logguer.info("--" * 20)
        return False
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la configuration de PostgreSQL : {e}")
        logguer.critical(f"Erreur critique lors de la configuration de PostgreSQL: {e}")
        logguer.info("--" * 20)
        return False


def create_database():
    """ Crée la base de données MyDataBase si elle n'existe pas """
    try:
        logguer.info('Creation de la base données...')
        conn = psycopg2.connect(dbname="postgres", user=PG_ADMIN_USER, password=PG_ADMIN_PASSWORD, host=PG_HOST, port=PG_PORT)
        conn.autocommit = True
        cur = conn.cursor()

        # Vérifier si la base existe déjà
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if cur.fetchone():
            print(f"La base de données {DB_NAME} existe déjà.")
            logguer.info(f"La base de données {DB_NAME} existe déjà.")
        else:
            cur.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Base de données {DB_NAME} créée avec succès.")
            logguer.info(f"Base de données {DB_NAME} créée avec succès.")

        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de la base de données : {e}")
        logguer.critical("Une erreur s'est produit lors de la création de la base de données.")
    logguer.info("--" * 20)
def restore_database():
    """ Restaure la base de données depuis un fichier dump """
    logguer.info("Restauration de la base de données... ")
    try:
        system_platform = platform.system()
        # Vérifier si le fichier existe
        if not os.path.exists(BACKUP_FILE):
            print(f"Erreur : Le fichier de sauvegarde {BACKUP_FILE} n'existe pas.")
            logguer.error(f"Erreur : Le fichier de sauvegarde {BACKUP_FILE} n'existe pas.")
            return
        # Construire la commande pg_restore
        if system_platform == "Windows":
            print(f"voici le chemin de restauration: {BACKUP_FILE}")
            # Windows : Utilisation de guillemets pour éviter les erreurs de chemin
            command = f'pg_restore -U {PG_ADMIN_USER} -d {DB_NAME} -h {PG_HOST} -p {PG_PORT} "{BACKUP_FILE}"'
        else:
            # Linux/macOS : Utilisation normale
            command = f'PGPASSWORD={PG_ADMIN_PASSWORD} pg_restore -U {PG_ADMIN_USER} -d {DB_NAME} -h {PG_HOST} -p {PG_PORT} {BACKUP_FILE}'
        # Exécuter la commande
        subprocess.run(command, shell=True, check=True, env=postgres_pass_env)
        print(f"Restauration de la base de données {DB_NAME} terminée avec succès depuis {BACKUP_FILE}.")
        logguer.info(f"Restauration de la base de données {DB_NAME} terminée avec succès depuis {BACKUP_FILE}.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la restauration de la base de données : {e}")
        logguer.error(f"Erreur lors de la restauration de la base de données : {e}")

    logguer.info("--" * 20)
if __name__ == '__main__':
    #initialiser_config()
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
                        "resources", "database", "gestion_boutique.sql")
    # Test
    if is_postgresql_installed_and_setup():
        create_database()
        restore_database()
