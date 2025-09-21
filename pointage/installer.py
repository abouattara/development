# =============================================================================
# FICHIER: installer.py (Script d'installation)
# =============================================================================

"""
Script d'installation pour l'application de pointage
"""

import os
import sys
import subprocess
import shutil

def install_dependencies():
    """Installe les dépendances Python"""
    dependencies = [
        "Pillow>=9.0.0",
        "openpyxl>=3.0.0"
    ]
    
    print("Installation des dépendances...")
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep} installé")
        except subprocess.CalledProcessError:
            print(f"✗ Erreur lors de l'installation de {dep}")
            return False
    
    return True

def create_directories():
    """Crée les dossiers nécessaires"""
    directories = ["rapports", "logs", "sauvegardes"]
    
    print("Création des dossiers...")
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Dossier {directory} créé")
        except Exception as e:
            print(f"✗ Erreur lors de la création du dossier {directory}: {e}")

def create_desktop_shortcut():
    """Crée un raccourci sur le bureau (Windows uniquement)"""
    if sys.platform == "win32":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Pointage Empreintes.lnk")
            target = os.path.join(os.getcwd(), "main_gui.py")
            wDir = os.getcwd()
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.save()
            
            print("✓ Raccourci créé sur le bureau")
        except ImportError:
            print("! Raccourci non créé (winshell non disponible)")
        except Exception as e:
            print(f"! Erreur lors de la création du raccourci: {e}")

def main():
    """Installation principale"""
    print("=== INSTALLATION DE L'APPLICATION DE POINTAGE ===\n")
    
    # Vérification de Python
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 ou supérieur requis")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    
    # Installation des dépendances
    if not install_dependencies():
        print("\n✗ Échec de l'installation des dépendances")
        return False
    
    # Création des dossiers
    create_directories()
    
    # Test de l'application
    print("\nTest de l'application...")
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        print("✓ Base de données initialisée")
        
        from fingerprint_manager import FingerprintManager
        fp = FingerprintManager()
        print("✓ Gestionnaire d'empreintes initialisé")
        
        from excel_generator import ExcelGenerator
        excel = ExcelGenerator()
        print("✓ Générateur Excel initialisé")
        
    except Exception as e:
        print(f"✗ Erreur lors du test: {e}")
        return False
    
    # Création du raccourci
    create_desktop_shortcut()
    
    print("\n=== INSTALLATION TERMINÉE AVEC SUCCÈS ===")
    print("Pour lancer l'application: python main_gui.py")
    
    return True

if __name__ == "__main__":
    if main():
        input("\nAppuyez sur Entrée pour continuer...")
    else:
        input("\nInstallation échouée. Appuyez sur Entrée pour quitter...")