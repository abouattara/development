# =============================================================================
# FICHIER: config.py (Configuration)
# =============================================================================

"""
Configuration de l'application de pointage
"""

import os
from datetime import datetime

class Config:
    """Configuration générale de l'application"""
    
    # Base de données
    DATABASE_PATH = "pointage.db"
    
    # Dossiers
    REPORTS_DIR = "rapports"
    LOGS_DIR = "logs"
    BACKUPS_DIR = "sauvegardes"
    
    # Empreintes
    FINGERPRINT_THRESHOLD = 0.8  # Seuil de correspondance
    FINGERPRINT_TIMEOUT = 10     # Timeout de capture en secondes
    
    # Interface
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    
    # Rapports
    EXCEL_TEMPLATE = "template_rapport.xlsx"
    
    @classmethod
    def init_directories(cls):
        """Initialise les dossiers nécessaires"""
        for directory in [cls.REPORTS_DIR, cls.LOGS_DIR, cls.BACKUPS_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    @classmethod
    def get_backup_filename(cls):
        """Génère un nom de fichier de sauvegarde"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(cls.BACKUPS_DIR, f"pointage_backup_{timestamp}.db")
