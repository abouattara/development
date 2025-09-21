# Application de Pointage par Empreintes Digitales

## Description

Application desktop Python permettant le pointage automatisé lors de réunions via reconnaissance d'empreintes digitales.

## Fonctionnalités principales

- Gestion complète des membres et leurs empreintes
- Création et gestion des réunions
- Pointage en temps réel par reconnaissance d'empreintes
- Génération automatique de rapports Excel
- Interface graphique intuitive

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Windows 10/11, Linux Ubuntu 18.04+ ou macOS

### Installation des dépendances

```bash
pip install Pillow openpyxl
```

### Lancement de l'application

```bash
python main_gui.py
```

## Structure de la base de données

### Table Membre

- id_empreinte (TEXT PRIMARY KEY)
- titre, nom, prenom (TEXT)
- service, email, telephone (TEXT)
- empreinte_data (BLOB)
- empreinte_hash (TEXT)
- date_creation (TIMESTAMP)
- actif (BOOLEAN)

### Table Reunion

- id_reunion (INTEGER PRIMARY KEY)
- titre_reunion, lieu (TEXT)
- date_reunion (TIMESTAMP)
- statut (TEXT)

### Table Participation

- id_participation (INTEGER PRIMARY KEY)
- id_reunion, id_empreinte (FOREIGN KEYS)
- heure_pointage (TIMESTAMP)
- methode_pointage (TEXT)

## Utilisation

### 1. Gestion des membres

1. Aller dans l'onglet "Gestion des Membres"
2. Remplir les informations du membre
3. Cliquer sur "Capturer Empreinte"
4. Cliquer sur "Ajouter Membre"

### 2. Création d'une réunion

1. Aller dans l'onglet "Gestion des Réunions"
2. Saisir le titre, lieu, date et heure
3. Cliquer sur "Créer la Réunion"

### 3. Pointage

1. Aller dans l'onglet "Pointage"
2. Sélectionner la réunion active
3. Cliquer sur "Scanner Empreinte"
4. Confirmer le pointage

### 4. Génération de rapports

1. Aller dans l'onglet "Rapports"
2. Sélectionner une réunion
3. Prévisualiser ou générer le fichier Excel

## Mode simulation

L'application fonctionne en mode simulation par défaut (sans lecteur physique).
Pour intégrer un vrai lecteur d'empreintes, modifier la classe FingerprintManager.

## Sécurité

- Les empreintes sont stockées sous forme de hash
- Sauvegarde automatique de la base de données
- Logs d'audit des opérations

## Support

Pour toute question ou problème, consulter le cahier des charges complet.
