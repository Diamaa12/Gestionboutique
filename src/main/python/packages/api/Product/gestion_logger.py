from logging.handlers import RotatingFileHandler, SMTPHandler
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

max_bytes = 1024 * 1024 * 5
chemin_fichier_log = Path(os.getenv("PROGRAMDATA")) / "BBLTech/logs"  # Recupérer le chemin en utilisant getenv
chemin_fichier_log.mkdir(parents=True, exist_ok=True)  # Créer le dossier si nécessaire

# Charger les variables du fichier .env
#cibler le fichier .env
env_path = Path(__file__).parent.parent.parent.parent.parent.parent.absolute() / 'Envdir/.env'
load_dotenv(dotenv_path=env_path)  # Charge les variables du .env dans les variables d'environnement

# Récupérer les identifiants et autres paramètres depuis les variables d'environnement
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))
use_tls = os.getenv('USE_TLS')
recipient_email = os.getenv('RECIPIENT_EMAIL')



def setup_logger_with_rotation(name, log_file, max_bytes=max_bytes, backup_count=10):
    if not all([email, password, smtp_server, smtp_port, recipient_email]):
        raise ValueError("Les variables d'environnement SMTP et/ou email sont manquantes.")
    """Configurer un logger avec rotation."""

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Création d'un gestionnaire qui écrit dans un fichier avec rotation
    handler = RotatingFileHandler(f"{chemin_fichier_log}/{log_file}",  # Fichier dans lequel écrire
                                  maxBytes=max_bytes,  # Taille maximale de 5 Mo avant rotation
                                  backupCount=backup_count  #Fichiers Maximum à sauvegarder avant rotation
)
    # Création d'un logger
    # On donne un nom au logger, ici 'mon_logger'
    logger = logging.getLogger(name)
    # Configuration du gestionnaire d'e-mails
    mail_handler = SMTPHandler(
        mailhost=(smtp_server, smtp_port),
        fromaddr=email,
        toaddrs=[recipient_email],
        subject="Une erreure critique au niveau de l'application BBLTech",
        credentials=(email, password),
        secure=() if use_tls else None # Active TLS

    )
    #On definie le niveau du logger
    mail_handler.setLevel(logging.CRITICAL)
    # On  défini le niveau minimal des logs (DEBUG, INFO, etc.)
    logger.setLevel(logging.DEBUG)
    # Configuration du format des messages de log
    handler.setFormatter(formatter)
    mail_handler.setFormatter(formatter)
    # Associer le gestionnaire au logger
    logger.addHandler(handler)
    logger.addHandler(mail_handler)

    return logger


# Exemple d'utilisation
if __name__ == "__main__":
    main_logger = setup_logger_with_rotation('Test', 'test.log')
    main_logger.info('Message d\'information')
    main_logger.warning('Message d\'avertissement')
    main_logger.error('Message d\'erreur')
    main_logger.critical('Message de critique')
    print(env_path)
