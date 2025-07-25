import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

class FallbackService:
    """Service de fallback utilisant le système de fichiers local"""
    
    def __init__(self):
        self.data_dir = "data/free_analysis"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Crée le répertoire de données s'il n'existe pas"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_client_file_path(self, client_id: str) -> str:
        """Génère le chemin du fichier pour un client"""
        return os.path.join(self.data_dir, f"{client_id}.json")
    
    def _get_stats_file_path(self) -> str:
        """Génère le chemin du fichier de statistiques"""
        return os.path.join(self.data_dir, "stats.json")
    
    def check_free_analysis_available(self, client_id: str) -> bool:
        """Vérifie si le client peut faire une analyse gratuite"""
        try:
            file_path = self._get_client_file_path(client_id)
            if not os.path.exists(file_path):
                return True
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Vérifier l'expiration
            expires_at = datetime.fromisoformat(data['expires_at'])
            if datetime.now() > expires_at:
                # Supprimer le fichier expiré
                os.remove(file_path)
                return True
            
            return False
        except Exception as e:
            print(f"Erreur Fallback lors de la vérification: {e}")
            return True  # En cas d'erreur, permettre l'analyse
    
    def mark_free_analysis_used(self, client_id: str) -> bool:
        """Marque l'analyse gratuite comme utilisée pour ce client"""
        try:
            file_path = self._get_client_file_path(client_id)
            expiry = timedelta(hours=24)
            
            data = {
                "used_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + expiry).isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Incrémenter les statistiques
            self._increment_stats()
            
            return True
        except Exception as e:
            print(f"Erreur Fallback lors du marquage: {e}")
            return False
    
    def get_free_analysis_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations sur l'analyse gratuite d'un client"""
        try:
            file_path = self._get_client_file_path(client_id)
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur Fallback lors de la récupération: {e}")
            return None
    
    def reset_free_analysis(self, client_id: str) -> bool:
        """Réinitialise l'analyse gratuite pour un client"""
        try:
            file_path = self._get_client_file_path(client_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Erreur Fallback lors de la réinitialisation: {e}")
            return False
    
    def _increment_stats(self):
        """Incrémente les statistiques globales"""
        try:
            stats_file = self._get_stats_file_path()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Charger les statistiques existantes
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            else:
                stats = {
                    "total_free_analyses": 0,
                    "daily_stats": {}
                }
            
            # Incrémenter les compteurs
            stats["total_free_analyses"] += 1
            if today not in stats["daily_stats"]:
                stats["daily_stats"][today] = 0
            stats["daily_stats"][today] += 1
            
            # Nettoyer les anciennes statistiques quotidiennes (plus de 30 jours)
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            stats["daily_stats"] = {
                date: count for date, count in stats["daily_stats"].items()
                if date >= cutoff_date
            }
            
            # Sauvegarder les statistiques
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            print(f"Erreur Fallback lors de l'incrémentation des stats: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales"""
        try:
            stats_file = self._get_stats_file_path()
            today = datetime.now().strftime("%Y-%m-%d")
            
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                
                return {
                    "total_free_analyses": stats.get("total_free_analyses", 0),
                    "today_free_analyses": stats.get("daily_stats", {}).get(today, 0),
                    "date": today
                }
            else:
                return {
                    "total_free_analyses": 0,
                    "today_free_analyses": 0,
                    "date": today
                }
        except Exception as e:
            print(f"Erreur Fallback lors de la récupération des stats: {e}")
            return {
                "total_free_analyses": 0,
                "today_free_analyses": 0,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
    
    def cleanup_expired_entries(self) -> int:
        """Nettoie les entrées expirées"""
        try:
            cleaned_count = 0
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json') and filename != 'stats.json':
                    file_path = os.path.join(self.data_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        expires_at = datetime.fromisoformat(data['expires_at'])
                        if datetime.now() > expires_at:
                            os.remove(file_path)
                            cleaned_count += 1
                    except Exception:
                        # Supprimer les fichiers corrompus
                        os.remove(file_path)
                        cleaned_count += 1
            
            return cleaned_count
        except Exception as e:
            print(f"Erreur Fallback lors du nettoyage: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Vérifie la santé du service de fallback"""
        try:
            # Tester l'écriture et lecture
            test_file = os.path.join(self.data_dir, "health_test.json")
            test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
            
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            
            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            
            os.remove(test_file)
            
            return loaded_data["test"] == "data"
        except Exception as e:
            print(f"Erreur Fallback health check: {e}")
            return False

# Instance globale du service de fallback
fallback_service = FallbackService() 