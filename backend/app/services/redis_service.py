import redis
import json
from datetime import datetime, timedelta
from app.config import settings
from typing import Optional, Dict, Any
from app.services.fallback_service import fallback_service

class RedisService:
    def __init__(self):
        self.redis_available = False
        redis_url = "redis://:2bD5L6pTEKkwtDyF08q7HuqtmojbgeIr@redis-12662.crce202.eu-west-3-1.ec2.redns.redis-cloud.com:12662"
        redis_password = "2bD5L6pTEKkwtDyF08q7HuqtmojbgeIr"
        redis_db = 0
        try:
            self.redis_client = redis.from_url(
                redis_url,
                password=redis_password,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Tester la connexion
            self.redis_client.ping()
            self.redis_available = True
            print("✅ Redis connecté avec succès")
        except Exception as e:
            print(f"⚠️ Redis non disponible, utilisation du fallback: {e}")
            self.redis_available = False
    
    def _get_free_analysis_key(self, client_id: str) -> str:
        """Génère la clé Redis pour l'analyse gratuite d'un client"""
        return f"free_analysis:{client_id}"
    
    def _get_free_analysis_stats_key(self) -> str:
        """Génère la clé Redis pour les statistiques globales"""
        return "free_analysis:stats"
    
    def check_free_analysis_available(self, client_id: str) -> bool:
        """Vérifie si le client peut faire une analyse gratuite"""
        if not self.redis_available:
            return fallback_service.check_free_analysis_available(client_id)
        
        try:
            key = self._get_free_analysis_key(client_id)
            exists = self.redis_client.exists(key)
            return not exists
        except Exception as e:
            print(f"Erreur Redis lors de la vérification, utilisation du fallback: {e}")
            return fallback_service.check_free_analysis_available(client_id)
    
    def mark_free_analysis_used(self, client_id: str) -> bool:
        """Marque l'analyse gratuite comme utilisée pour ce client"""
        if not self.redis_available:
            return fallback_service.mark_free_analysis_used(client_id)
        
        try:
            key = self._get_free_analysis_key(client_id)
            # Stocker avec expiration de 24h
            expiry = timedelta(hours=24)
            
            data = {
                "used_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + expiry).isoformat()
            }
            
            # Stocker les données
            self.redis_client.setex(
                key,
                int(expiry.total_seconds()),
                json.dumps(data)
            )
            
            # Incrémenter les statistiques
            self._increment_stats()
            
            return True
        except Exception as e:
            print(f"Erreur Redis lors du marquage, utilisation du fallback: {e}")
            return fallback_service.mark_free_analysis_used(client_id)
    
    def get_free_analysis_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations sur l'analyse gratuite d'un client"""
        if not self.redis_available:
            return fallback_service.get_free_analysis_info(client_id)
        
        try:
            key = self._get_free_analysis_key(client_id)
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Erreur Redis lors de la récupération, utilisation du fallback: {e}")
            return fallback_service.get_free_analysis_info(client_id)
    
    def reset_free_analysis(self, client_id: str) -> bool:
        """Réinitialise l'analyse gratuite pour un client (pour les tests)"""
        if not self.redis_available:
            return fallback_service.reset_free_analysis(client_id)
        
        try:
            key = self._get_free_analysis_key(client_id)
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Erreur Redis lors de la réinitialisation, utilisation du fallback: {e}")
            return fallback_service.reset_free_analysis(client_id)
    
    def _increment_stats(self):
        """Incrémente les statistiques globales"""
        try:
            stats_key = self._get_free_analysis_stats_key()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Incrémenter le compteur global
            self.redis_client.incr(f"{stats_key}:total")
            
            # Incrémenter le compteur quotidien
            self.redis_client.incr(f"{stats_key}:daily:{today}")
            
            # Expirer les stats quotidiennes après 30 jours
            self.redis_client.expire(f"{stats_key}:daily:{today}", 30 * 24 * 3600)
            
        except Exception as e:
            print(f"Erreur Redis lors de l'incrémentation des stats: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales"""
        if not self.redis_available:
            return fallback_service.get_stats()
        
        try:
            stats_key = self._get_free_analysis_stats_key()
            today = datetime.now().strftime("%Y-%m-%d")
            
            total = self.redis_client.get(f"{stats_key}:total") or "0"
            daily = self.redis_client.get(f"{stats_key}:daily:{today}") or "0"
            
            return {
                "total_free_analyses": int(total),
                "today_free_analyses": int(daily),
                "date": today
            }
        except Exception as e:
            print(f"Erreur Redis lors de la récupération des stats, utilisation du fallback: {e}")
            return fallback_service.get_stats()
    
    def cleanup_expired_entries(self) -> int:
        """Nettoie les entrées expirées (appelé périodiquement)"""
        try:
            # Redis gère automatiquement l'expiration avec TTL
            # Cette fonction peut être utilisée pour des nettoyages supplémentaires
            return 0
        except Exception as e:
            print(f"Erreur Redis lors du nettoyage: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Redis"""
        if not self.redis_available:
            return fallback_service.health_check()
        
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            print(f"Erreur Redis health check: {e}")
            return fallback_service.health_check()

# Instance globale du service Redis
redis_service = RedisService() 