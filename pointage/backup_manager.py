# =============================================================================
# FICHIER: backup_manager.py (Gestionnaire de sauvegardes)
# =============================================================================

import shutil
import os
from datetime import datetime, timedelta
import sqlite3

class BackupManager:
    """Gestionnaire de sauvegardes de la base de données"""
    
    def __init__(self, db_path="pointage.db", backup_dir="sauvegardes"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self):
        """Crée une sauvegarde de la base de données"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"pointage_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copie de la base de données
            shutil.copy2(self.db_path, backup_path)
            
            return backup_path
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return None
    
    def auto_backup(self):
        """Sauvegarde automatique quotidienne"""
        today = datetime.now().strftime('%Y%m%d')
        
        # Vérifier si une sauvegarde existe déjà aujourd'hui
        existing_backups = [f for f in os.listdir(self.backup_dir) 
                           if f.startswith(f"pointage_backup_{today}")]
        
        if not existing_backups:
            return self.create_backup()
        return None
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Supprime les anciennes sauvegardes"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("pointage_backup_"):
                file_path = os.path.join(self.backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        print(f"Ancienne sauvegarde supprimée: {filename}")
                    except Exception as e:
                        print(f"Erreur lors de la suppression de {filename}: {e}")
    
    def restore_backup(self, backup_path):
        """Restaure une sauvegarde"""
        try:
            # Vérifier que le fichier de sauvegarde est valide
            conn = sqlite3.connect(backup_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            conn.close()
            
            # Créer une sauvegarde de la base actuelle
            current_backup = self.create_backup()
            
            if current_backup:
                # Restaurer la sauvegarde
                shutil.copy2(backup_path, self.db_path)
                return True
            
        except Exception as e:
            print(f"Erreur lors de la restauration: {e}")
        
        return False