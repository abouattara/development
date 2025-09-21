# =============================================================================
# FICHIER: database.py - Gestion de la base de données
# =============================================================================

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    """Gestionnaire de base de données pour l'application de pointage"""
    
    def __init__(self, db_path: str = "pointage.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table Membre
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Membre (
            id_empreinte TEXT PRIMARY KEY,
            titre TEXT NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            service TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT,
            empreinte_data BLOB,
            empreinte_hash TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actif BOOLEAN DEFAULT 1
        )
        ''')
        
        # Table Reunion
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reunion (
            id_reunion INTEGER PRIMARY KEY AUTOINCREMENT,
            titre_reunion TEXT NOT NULL,
            lieu TEXT NOT NULL,
            date_reunion TIMESTAMP NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'planifiee'
        )
        ''')
        
        # Table Participation
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Participation (
            id_participation INTEGER PRIMARY KEY AUTOINCREMENT,
            id_reunion INTEGER,
            id_empreinte TEXT,
            heure_pointage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            methode_pointage TEXT DEFAULT 'empreinte',
            FOREIGN KEY (id_reunion) REFERENCES Reunion(id_reunion),
            FOREIGN KEY (id_empreinte) REFERENCES Membre(id_empreinte)
        )
        ''')
        
        # Index pour performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reunion_date ON Reunion(date_reunion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_participation_reunion ON Participation(id_reunion)')
        
        conn.commit()
        conn.close()
    
    def add_membre(self, membre_data: Dict) -> bool:
        """Ajoute un nouveau membre"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Génération de l'ID empreinte
            id_empreinte = self.generate_fingerprint_id(membre_data['nom'], membre_data['prenom'])
            
            cursor.execute('''
            INSERT INTO Membre (id_empreinte, titre, nom, prenom, service, email, telephone, empreinte_data, empreinte_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                id_empreinte,
                membre_data['titre'],
                membre_data['nom'],
                membre_data['prenom'],
                membre_data['service'],
                membre_data['email'],
                membre_data.get('telephone', ''),
                membre_data.get('empreinte_data'),
                membre_data.get('empreinte_hash')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout du membre: {e}")
            return False
    
    def get_all_membres(self) -> List[Dict]:
        """Récupère tous les membres actifs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id_empreinte, titre, nom, prenom, service, email, telephone, date_creation
        FROM Membre WHERE actif = 1
        ORDER BY nom, prenom
        ''')
        
        membres = []
        for row in cursor.fetchall():
            membres.append({
                'id_empreinte': row[0],
                'titre': row[1],
                'nom': row[2],
                'prenom': row[3],
                'service': row[4],
                'email': row[5],
                'telephone': row[6],
                'date_creation': row[7]
            })
        
        conn.close()
        return membres
    
    def update_membre(self, id_empreinte: str, membre_data: Dict) -> bool:
        """Met à jour un membre existant"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE Membre SET titre=?, nom=?, prenom=?, service=?, email=?, telephone=?
            WHERE id_empreinte=?
            ''', (
                membre_data['titre'],
                membre_data['nom'],
                membre_data['prenom'],
                membre_data['service'],
                membre_data['email'],
                membre_data.get('telephone', ''),
                id_empreinte
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour: {e}")
            return False
    
    def create_reunion(self, reunion_data: Dict) -> int:
        """Crée une nouvelle réunion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO Reunion (titre_reunion, lieu, date_reunion)
        VALUES (?, ?, ?)
        ''', (
            reunion_data['titre'],
            reunion_data['lieu'],
            reunion_data['date']
        ))
        
        reunion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reunion_id
    
    def get_reunions(self) -> List[Dict]:
        """Récupère toutes les réunions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id_reunion, titre_reunion, lieu, date_reunion, statut
        FROM Reunion
        ORDER BY date_reunion DESC
        ''')
        
        reunions = []
        for row in cursor.fetchall():
            reunions.append({
                'id_reunion': row[0],
                'titre': row[1],
                'lieu': row[2],
                'date': row[3],
                'statut': row[4]
            })
        
        conn.close()
        return reunions
    
    def add_participation(self, id_reunion: int, id_empreinte: str) -> bool:
        """Enregistre une participation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier si déjà pointé
            cursor.execute('''
            SELECT id_participation FROM Participation 
            WHERE id_reunion=? AND id_empreinte=?
            ''', (id_reunion, id_empreinte))
            
            if cursor.fetchone():
                conn.close()
                return False  # Déjà pointé
            
            cursor.execute('''
            INSERT INTO Participation (id_reunion, id_empreinte)
            VALUES (?, ?)
            ''', (id_reunion, id_empreinte))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la participation: {e}")
            return False
    
    def get_participants(self, id_reunion: int) -> List[Dict]:
        """Récupère les participants d'une réunion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT m.titre, m.nom, m.prenom, m.service, m.email, m.telephone, p.heure_pointage
        FROM Participation p
        JOIN Membre m ON p.id_empreinte = m.id_empreinte
        WHERE p.id_reunion = ?
        ORDER BY p.heure_pointage
        ''', (id_reunion,))
        
        participants = []
        for row in cursor.fetchall():
            participants.append({
                'titre': row[0],
                'nom': row[1],
                'prenom': row[2],
                'service': row[3],
                'email': row[4],
                'telephone': row[5],
                'heure_pointage': row[6]
            })
        
        conn.close()
        return participants
    
    def find_membre_by_fingerprint(self, fingerprint_hash: str) -> Optional[Dict]:
        """Trouve un membre par son empreinte"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id_empreinte, titre, nom, prenom, service, email, telephone
        FROM Membre 
        WHERE empreinte_hash = ? AND actif = 1
        ''', (fingerprint_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id_empreinte': row[0],
                'titre': row[1],
                'nom': row[2],
                'prenom': row[3],
                'service': row[4],
                'email': row[5],
                'telephone': row[6]
            }
        return None
    
    def generate_fingerprint_id(self, nom: str, prenom: str) -> str:
        """Génère un ID unique pour l'empreinte"""
        base = f"{nom.upper()}{prenom.upper()}{datetime.now().isoformat()}"
        return hashlib.md5(base.encode()).hexdigest()[:16]
    
    def update_reunion_status(self, id_reunion: int, statut: str) -> bool:
        """Met à jour le statut d'une réunion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE Reunion SET statut = ? WHERE id_reunion = ?
            ''', (statut, id_reunion))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False

