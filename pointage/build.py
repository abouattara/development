# =============================================================================
# FICHIER: build.py (Création d'un exécutable)
# =============================================================================

"""
Script pour créer un exécutable de l'application
Utilise PyInstaller pour packager l'application
"""

import os
import sys
import subprocess

def build_executable():
    """Crée un exécutable avec PyInstaller"""
    
    # Vérifier si PyInstaller est installé
    try:
        import PyInstaller
    except ImportError:
        print("Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Commande PyInstaller
    cmd = [
        "pyinstaller",
        "--onedir",                    # Un dossier avec tous les fichiers
        "--windowed",                  # Pas de console
        "--name=PointageEmpreintes",   # Nom de l'exécutable
        "--icon=icon.ico",             # Icône (si disponible)
        "--add-data=pointage.db;.",    # Inclure la base de données
        "main_gui.py"                  # Script principal
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Exécutable créé dans le dossier 'dist'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erreur lors de la création de l'exécutable: {e}")
        return False

if __name__ == "__main__":
    print("=== CRÉATION DE L'EXÉCUTABLE ===\n")
    
    if build_executable():
        print("\n=== CRÉATION TERMINÉE ===")
        print("L'exécutable se trouve dans le dossier 'dist/PointageEmpreintes/'")
    else:
        print("\n=== ÉCHEC DE LA CRÉATION ===")
    
    input("\nAppuyez sur Entrée pour continuer...")
