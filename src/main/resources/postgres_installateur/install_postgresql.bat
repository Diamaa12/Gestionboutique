@echo off
echo Installation de PostgreSQL en cours...

:: Définir le mot de passe du superutilisateur PostgreSQL
set PGPASSWORD=Galle11

:: Définir le nom du fichier de l’installateur PostgreSQL (qui est dans le même dossier que ce script)
set INSTALLER_NAME=postgresql-17.2-3-windows-x64.exe

:: Vérifier si l’installateur existe
if not exist "%~dp0%INSTALLER_NAME%" (
    echo Erreur : L'installateur PostgreSQL est introuvable ! >> "%~dp0install_log.txt"
    exit /b 1
)

:: Afficher un message avant de commencer l'installation
echo Lancement de l'installation de PostgreSQL... >> "%~dp0install_log.txt"
echo Lancement de l'installation de PostgreSQL...

:: Lancer l’installateur PostgreSQL en mode silencieux et rediriger la sortie et erreurs vers un fichier
start /wait "%~dp0%INSTALLER_NAME%" >> "%~dp0install_log.txt" 2>&1

:: Vérifier si l'installation a réussi
if %ERRORLEVEL% neq 0 (
    echo Erreur lors de l'installation de PostgreSQL. >> "%~dp0install_log.txt"
    echo Erreur lors de l'installation de PostgreSQL.
    exit /b 1
)

:: Ajouter PostgreSQL au PATH et journaliser l'action
echo Ajout de PostgreSQL au PATH... >> "%~dp0install_log.txt"
setx PATH "%PATH%;C:\Program Files\PostgreSQL\17\bin" >> "%~dp0install_log.txt" 2>&1

:: Afficher un message de succès
echo PostgreSQL a été installé avec succès ! >> "%~dp0install_log.txt"
echo PostgreSQL a été installé avec succès !

exit /b 0
:: Ouvrir le fichier journal après l'exécution
echo Affichage du fichier journal...
type "%~dp0install_log.txt"
pause