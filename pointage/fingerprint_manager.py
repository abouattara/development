# =============================================================================
# FICHIER: fingerprint_manager.py - Gestion des empreintes
# =============================================================================

import hashlib
import random
from PIL import Image, ImageDraw
import io
from typing import Optional, Tuple

class FingerprintManager:
    """Gestionnaire d'empreintes digitales"""
    
    def __init__(self):
        self.device_connected = False
        self.simulate_device = True  # Mode simulation pour test
    
    def check_device(self) -> bool:
        """Vérifie la présence d'un lecteur d'empreintes"""
        # Simulation - dans un vrai projet, on utiliserait un SDK
        self.device_connected = True
        return self.device_connected
    
    def capture_fingerprint(self) -> Optional[Tuple[bytes, str]]:
        """Capture une empreinte et retourne les données et le hash"""
        if not self.device_connected and not self.simulate_device:
            return None
        
        # Simulation d'une capture d'empreinte
        if self.simulate_device:
            fingerprint_data = self.generate_simulated_fingerprint()
            fingerprint_hash = self.generate_fingerprint_hash(fingerprint_data)
            return fingerprint_data, fingerprint_hash
        
        # Ici, on intégrerait le vrai SDK du lecteur d'empreintes
        return None
    
    def generate_simulated_fingerprint(self) -> bytes:
        """Génère une empreinte simulée pour les tests"""
        # Crée une image BMP simple simulant une empreinte
        img = Image.new('RGB', (256, 256), 'white')
        draw = ImageDraw.Draw(img)
        
        # Dessine des lignes courbes simulant une empreinte
        for i in range(10):
            x1, y1 = random.randint(50, 200), random.randint(50, 200)
            x2, y2 = random.randint(50, 200), random.randint(50, 200)
            draw.line([x1, y1, x2, y2], fill='black', width=2)
        
        # Convertit en bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='BMP')
        return img_buffer.getvalue()
    
    def generate_fingerprint_hash(self, fingerprint_data: bytes) -> str:
        """Génère un hash unique pour l'empreinte"""
        return hashlib.sha256(fingerprint_data).hexdigest()
    
    def compare_fingerprints(self, hash1: str, hash2: str, threshold: float = 0.8) -> bool:
        """Compare deux empreintes (simulation)"""
        # Dans un vrai projet, on utiliserait un algorithme de comparaison biométrique
        # Ici, on simule avec une comparaison de hash
        if hash1 == hash2:
            return True
        
        # Simulation d'une correspondance partielle
        return random.random() > (1 - threshold) if hash1 and hash2 else False
    
    def save_fingerprint_image(self, fingerprint_data: bytes, filepath: str) -> bool:
        """Sauvegarde l'image d'empreinte"""
        try:
            with open(filepath, 'wb') as f:
                f.write(fingerprint_data)
            return True
        except:
            return False
