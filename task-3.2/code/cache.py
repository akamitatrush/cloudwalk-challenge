"""
🚀 Redis Cache Module
=====================
Phase 2: Performance - Cache para Transaction Guardian

Features:
- Cache de resultados de análise
- Rate limiting por IP/client
- Métricas de cache (hits/misses)
- TTL configurável
"""

import redis
import json
import hashlib
from typing import Optional, Any, Dict
from datetime import datetime
import os


class RedisCache:
    """Gerenciador de cache Redis para Transaction Guardian"""
    
    def __init__(
        self,
        host: str = None,
        port: int = 6379,
        db: int = 0,
        default_ttl: int = 300,  # 5 minutos
        prefix: str = "guardian"
    ):
        self.host = host or os.getenv("REDIS_HOST", "guardian-redis")
        self.port = port
        self.db = db
        self.default_ttl = default_ttl
        self.prefix = prefix
        
        # Métricas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }
        
        # Conectar ao Redis
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Testar conexão
            self.client.ping()
            self.connected = True
            print(f"✅ Redis conectado: {self.host}:{self.port}")
        except redis.ConnectionError as e:
            print(f"⚠️ Redis não disponível: {e}")
            self.client = None
            self.connected = False
    
    def _make_key(self, key: str) -> str:
        """Cria chave com prefixo"""
        return f"{self.prefix}:{key}"
    
    def _hash_data(self, data: Dict) -> str:
        """Cria hash de dados para usar como chave"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()[:12]
    
    # ============== CACHE BÁSICO ==============
    
    def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache"""
        if not self.connected:
            return None
        
        try:
            full_key = self._make_key(key)
            value = self.client.get(full_key)
            
            if value:
                self.stats["hits"] += 1
                return json.loads(value)
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            self.stats["errors"] += 1
            print(f"❌ Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Salva valor no cache"""
        if not self.connected:
            return False
        
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.default_ttl
            self.client.setex(full_key, ttl, json.dumps(value))
            self.stats["sets"] += 1
            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"❌ Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        if not self.connected:
            return False
        
        try:
            full_key = self._make_key(key)
            self.client.delete(full_key)
            return True
        except Exception as e:
            self.stats["errors"] += 1
            return False
    
    # ============== CACHE DE TRANSAÇÕES ==============
    
    def get_transaction_result(self, tx_data: Dict) -> Optional[Dict]:
        """Busca resultado de análise em cache"""
        key = f"tx:{self._hash_data(tx_data)}"
        return self.get(key)
    
    def set_transaction_result(self, tx_data: Dict, result: Dict, ttl: int = 60) -> bool:
        """Salva resultado de análise em cache (TTL curto - 60s)"""
        key = f"tx:{self._hash_data(tx_data)}"
        return self.set(key, result, ttl)
    
    # ============== RATE LIMITING ==============
    
    def check_rate_limit(
        self, 
        client_id: str, 
        limit: int = 100, 
        window: int = 60
    ) -> Dict[str, Any]:
        """
        Verifica rate limit para um cliente.
        
        Args:
            client_id: Identificador do cliente (IP, API key, etc)
            limit: Número máximo de requisições
            window: Janela de tempo em segundos
        
        Returns:
            Dict com allowed, remaining, reset_in
        """
        if not self.connected:
            return {"allowed": True, "remaining": limit, "reset_in": 0}
        
        try:
            key = self._make_key(f"ratelimit:{client_id}")
            
            # Usar pipeline para atomicidade
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.ttl(key)
            results = pipe.execute()
            
            current_count = results[0]
            ttl = results[1]
            
            # Definir TTL se for nova chave
            if ttl == -1:
                self.client.expire(key, window)
                ttl = window
            
            allowed = current_count <= limit
            remaining = max(0, limit - current_count)
            
            return {
                "allowed": allowed,
                "remaining": remaining,
                "reset_in": ttl if ttl > 0 else window,
                "current": current_count,
                "limit": limit
            }
        except Exception as e:
            self.stats["errors"] += 1
            print(f"❌ Rate limit error: {e}")
            return {"allowed": True, "remaining": limit, "reset_in": 0}
    
    # ============== MÉTRICAS ==============
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / max(total, 1)
        
        info = {}
        if self.connected:
            try:
                redis_info = self.client.info("memory")
                info = {
                    "used_memory": redis_info.get("used_memory_human", "N/A"),
                    "connected_clients": self.client.info("clients").get("connected_clients", 0)
                }
            except:
                pass
        
        return {
            "connected": self.connected,
            "host": f"{self.host}:{self.port}",
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "errors": self.stats["errors"],
            "hit_rate": round(hit_rate * 100, 2),
            "redis_info": info
        }
    
    def get_keys_count(self, pattern: str = "*") -> int:
        """Conta chaves que correspondem ao padrão"""
        if not self.connected:
            return 0
        
        try:
            full_pattern = self._make_key(pattern)
            return len(self.client.keys(full_pattern))
        except:
            return 0
    
    # ============== CIRCUIT BREAKER STATE ==============
    
    def get_circuit_state(self, service: str) -> str:
        """Obtém estado do circuit breaker"""
        state = self.get(f"circuit:{service}")
        return state.get("state", "closed") if state else "closed"
    
    def set_circuit_state(
        self, 
        service: str, 
        state: str, 
        failures: int = 0,
        ttl: int = 300
    ) -> bool:
        """Define estado do circuit breaker"""
        return self.set(f"circuit:{service}", {
            "state": state,
            "failures": failures,
            "updated_at": datetime.now().isoformat()
        }, ttl)


# Singleton para uso global
_cache_instance = None

def get_cache() -> RedisCache:
    """Retorna instância singleton do cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
