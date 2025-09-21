# =============================================================================
# FICHIER: logger.py (Système de logs)
# =============================================================================

import logging
import os
from datetime import datetime

class Logger:
    """Gestionnaire de logs pour l'application"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configuration du logger
        log_filename = os.path.join(log_dir, f"pointage_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def info(self, message):
        """Log d'information"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log d'avertissement"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log d'erreur"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log de debug"""
        self.logger.debug(message)
