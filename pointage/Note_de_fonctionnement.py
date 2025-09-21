# Application de Pointage par Empreinte Digitale

# =============================================================================
# UTILISATION ET DÉPLOIEMENT
# =============================================================================

"""
GUIDE D'UTILISATION:

1. INSTALLATION:
   - Installer Python 3.8+
   - Exécuter: python installer.py
   - Ou manuellement: pip install Pillow openpyxl

2. LANCEMENT:
   - python main_gui.py
   - Ou double-cliquer sur le raccourci créé

3. PREMIÈRE UTILISATION:
   - Ajouter des membres avec leurs empreintes
   - Créer une réunion
   - Commencer le pointage

4. FONCTIONNALITÉS:
   - Gestion complète des membres
   - Création et suivi des réunions
   - Pointage en temps réel
   - Génération de rapports Excel
   - Sauvegarde automatique

5. FICHIERS GÉNÉRÉS:
   - pointage.db : Base de données
   - rapports/ : Fichiers Excel générés
   - logs/ : Fichiers de log
   - sauvegardes/ : Sauvegardes automatiques

6. MAINTENANCE:
   - Sauvegarde quotidienne automatique
   - Nettoyage des anciennes sauvegardes
   - Logs d'activité

7. DÉPLOIEMENT:
   - Copier tous les fichiers Python
   - Installer les dépendances
   - Ou utiliser build.py pour créer un exécutable

NOTES IMPORTANTES:
- L'application fonctionne en mode simulation par défaut
- Pour un vrai lecteur d'empreintes, modifier FingerprintManager
- La base SQLite permet un déploiement simple
- Interface responsive et moderne
- Code modulaire et extensible
"""