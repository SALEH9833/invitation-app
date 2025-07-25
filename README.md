# Projet de Gestion d'Invitations Restaurant

Ce projet est une application web développée en Python avec le framework Flask. Elle a été réalisée dans le cadre d'un projet de stage pour digitaliser le processus de demande d'invitations au restaurant de l'entreprise Ciments du Maroc.

## Fonctionnalités

L'application est divisée en deux interfaces principales, chacune avec des rôles et des permissions spécifiques :

### 1. Interface Secrétariat
- **Authentification sécurisée** par email et mot de passe.
- **Tableau de bord** principal avec accès aux différentes fonctionnalités.
- **Création d'une nouvelle invitation** via un formulaire dynamique :
  - Ajout dynamique d'invités.
  - Calcul automatique des quantités de repas et boissons.
- **Téléchargement automatique d'un reçu PDF** après chaque création.
- **Notification par email** envoyée au responsable et au service de restauration, avec le PDF en pièce jointe.
- **Historique complet** des invitations créées, avec suivi du statut en temps réel (En attente, Acceptée, Refusée).
- **Page de statistiques** pour visualiser les données clés : nombre total d'invitations, décompte par statut et par société invitée.

### 2. Interface Restauration
- **Authentification sécurisée**.
- **Tableau de bord** affichant uniquement les invitations en attente de validation.
- Possibilité d'**accepter** ou de **refuser** chaque invitation, mettant à jour instantanément son statut pour le secrétariat.

### Fonctionnalités Transverses
- **Mode Sombre / Mode Clair** avec mémorisation du choix de l'utilisateur.
- Interface utilisateur responsive construite avec le framework **Bootstrap**.

## Technologies Utilisées

- **Backend :**
  - **Python 3**
  - **Flask** (Framework web)
  - **PostgreSQL** (Base de données relationnelle)
  - **SQLAlchemy** (ORM pour la communication avec la base de données)
  - **Flask-Migrate** (Pour la gestion des migrations de la base de données)
  - **Flask-Login** (Pour la gestion des sessions utilisateur)
  - **Flask-Mail** (Pour l'envoi d'emails)
  - **WeasyPrint** (Pour la génération de PDF à partir de HTML/CSS)
  - **python-dotenv** (Pour la gestion des variables d'environnement et des secrets)

- **Frontend :**
  - **HTML5** avec le moteur de templates **Jinja2**
  - **CSS3**
  - **JavaScript** (Pour le formulaire dynamique et le mode sombre)
  - **Bootstrap 5** (Framework CSS)

## Installation et Lancement

1.  **Cloner le projet** ou télécharger les fichiers.
2.  **Créer un environnement virtuel :**
    ```bash
    python -m venv venv
    ```
3.  **Activer l'environnement virtuel :**
    - Sur Windows : ``
    - Sur macOS/Linux : `source venv/bin/activate`
4.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configurer PostgreSQL :** Créez une base de données et un utilisateur, puis mettez à jour la ligne `SQLALCHEMY_DATABASE_URI` dans le fichier `config.py`.
6.  **Configurer les variables d'environnement :** Créez un fichier `.env` à la racine et ajoutez vos identifiants pour l'envoi d'emails :
    ```
    EMAIL_USER="votre_email@gmail.com"
    EMAIL_PASS="votre_mot_de_passe_application_google"
    ```
7.  **Appliquer les migrations de la base de données :**
    ```bash
    flask db upgrade
    ```
8.  **Créer les utilisateurs de test :**
    ```bash
    flask create-users
    ```
9.  **Lancer l'application :**
    ```bash
    flask run
    ```
L'application sera accessible à l'adresse `http://127.0.0.1:5000`.

---
*Développé par SALEH MAHAMAT SALEH*#   i n v i t a t i o n - a p p  
 