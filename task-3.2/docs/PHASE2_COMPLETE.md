# 🚀 Phase 2: Performance - Complete Documentation

> **Transaction Guardian v2.0 - Redis Cache Integration**

## 📋 Overview

This phase adds **Redis Cache** to improve API performance and add protection features.

### What Changed

| Aspect | Before (v1.0) | After (Phase 2) |
|--------|---------------|-----------------|
| Response time | ~50-100ms | **<10ms (cached)** |
| Rate limiting | None | **100 req/min per IP** |
| Cache | None | **Redis with TTL** |
| Repeated requests | Full processing | **Instant from cache** |

---

## 🔗 New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cache/stats` | GET | Cache statistics (hits, misses, hit rate) |
| `/cache/flush` | DELETE | Clear all cache (admin) |
| `/cache/keys` | GET | Count cached keys |

---

## 🐳 New Services

| Service | Port | URL |
|---------|------|-----|
| **Redis** | 6379 | Internal only |
| **Redis Commander** | 8081 | http://34.39.251.57:8081 |

---

## 📊 Performance Metrics

### Cache Statistics
```bash
curl http://34.39.251.57:8001/cache/stats
```

Response:
```json
{
  "connected": true,
  "host": "guardian-redis:6379",
  "hits": 150,
  "misses": 50,
  "sets": 50,
  "errors": 0,
  "hit_rate": 75.0,
  "redis_info": {
    "used_memory": "1.24M",
    "connected_clients": 2
  }
}
```

### Rate Limiting Headers

Every response includes:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 45
```

---

## 🔧 How Cache Works

1. **Request arrives** at `/transaction`
2. **Check cache** - hash of transaction data
3. **If cached** → Return immediately (`"cached": true`)
4. **If not cached** → Process, save to cache (TTL: 60s)

### Cache Key Strategy
```python
# Transaction data is hashed
key = f"guardian:tx:{md5(json.dumps(tx_data))[:12]}"
# Example: guardian:tx:a1b2c3d4e5f6
```

---

## 🛡️ Rate Limiting

- **Limit:** 100 requests per minute per IP
- **Window:** 60 seconds (sliding)
- **Response when exceeded:** HTTP 429
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45
}
```

---

## 📁 Files Added/Modified
```
task-3.2/
├── code/
│   ├── cache.py          # NEW: Redis cache module
│   ├── main.py           # MODIFIED: v2.0 with cache
│   └── main_v1.py        # BACKUP: Original v1.0
├── infrastructure/
│   ├── docker-compose.redis.yml  # NEW: Redis services
│   └── requirements.txt          # MODIFIED: Added redis
└── docs/
    └── PHASE2_COMPLETE.md        # NEW: This file
```

---

## 🚀 Quick Start

### Start Redis (if not running)
```bash
cd ~/cloudwalk-challenge/task-3.2/infrastructure
docker compose -f docker-compose.redis.yml up -d
```

### Rebuild API with cache
```bash
docker compose build guardian-api
docker compose up -d guardian-api
```

### Test cache
```bash
# First call - processed
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-01-28T10:00:00", "status": "approved", "count": 100}'

# Second call - from cache ("cached": true)
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-01-28T10:00:00", "status": "approved", "count": 100}'
```

---

## ✅ Phase 2 Checklist

- [x] Redis container running
- [x] Redis Commander UI
- [x] Cache module (cache.py)
- [x] API integration with cache
- [x] Rate limiting middleware
- [x] Cache stats endpoint
- [x] Prometheus metrics for cache
- [x] Documentation

---

## 📈 Monitoring

### Prometheus Metrics (new)
```
transaction_guardian_cache_hits
transaction_guardian_cache_misses
```

### Grafana Query Example
```promql
rate(transaction_guardian_cache_hits[5m]) / 
(rate(transaction_guardian_cache_hits[5m]) + rate(transaction_guardian_cache_misses[5m]))
```

---

## 🔜 Next Steps (Phase 3+)

| Phase | Focus | Items |
|-------|-------|-------|
| **Phase 3** | Security | OAuth2, JWT, Vault |
| **Phase 4** | MLOps | MLflow, Model versioning |
| **Phase 5** | Clawdbot | Telegram/WhatsApp bot |

---

## 👤 Author

**Sérgio Henrique**
- Email: sergio@lognullsec.com
- LinkedIn: [linkedin.com/in/akasergiosilva](https://linkedin.com/in/akasergiosilva)

---

**Phase 2 Complete** ✅ | Branch: `phase2-performance`
