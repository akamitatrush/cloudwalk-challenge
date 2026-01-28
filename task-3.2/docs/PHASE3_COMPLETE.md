# 🔐 Phase 3: Security - Complete Documentation

> **Transaction Guardian v2.1 - JWT & API Key Authentication**

## 📋 Overview

This phase adds **authentication and authorization** to protect API endpoints.

### What Changed

| Aspect | Before (v2.0) | After (Phase 3) |
|--------|---------------|-----------------|
| Authentication | None | **JWT + API Key** |
| Authorization | None | **Role-based (RBAC)** |
| Protected endpoints | 0 | `/auth/*` |
| Users | None | **3 default users** |

---

## 🔑 Authentication Methods

### 1. JWT Token (Recommended)
```bash
# Step 1: Login
curl -X POST http://34.39.251.57:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {"username": "admin", "role": "admin", "permissions": ["read","write","admin"]}
}

# Step 2: Use token
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  http://34.39.251.57:8001/auth/me
```

### 2. API Key (Simple)
```bash
# Use default API key
curl -H "X-API-Key: guardian-api-key-2024" \
  http://34.39.251.57:8001/auth/me
```

---

## 👥 Default Users

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | admin | read, write, admin |
| `operator` | `operator123` | operator | read, write |
| `viewer` | `viewer123` | viewer | read |

---

## 🔗 New Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/auth/login` | POST | ❌ | Get JWT token |
| `/auth/me` | GET | ✅ | Current user info |
| `/auth/api-keys` | POST | ✅ (admin) | Create API key |
| `/auth/api-keys` | GET | ✅ (admin) | List API keys |
| `/auth/stats` | GET | ✅ (admin) | Auth statistics |
| `/auth/logout` | POST | ✅ | Logout |

---

## 🛡️ Security Features

### JWT Configuration

| Setting | Value |
|---------|-------|
| Algorithm | HS256 |
| Expiration | 24 hours |
| Secret | Auto-generated (or env `JWT_SECRET`) |

### Rate Limiting (from Phase 2)

| Setting | Value |
|---------|-------|
| Limit | 100 requests/minute |
| Window | 60 seconds |
| Per | IP address |

---

## 📁 Files Added
```
task-3.2/
└── code/
    ├── auth.py           # Authentication module
    ├── auth_routes.py    # Auth endpoints
    └── main.py           # Updated with auth router
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom JWT secret
export JWT_SECRET="your-super-secret-key-here"

# Optional: Set Redis host
export REDIS_HOST="guardian-redis"
```

---

## 📊 Auth Statistics
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://34.39.251.57:8001/auth/stats
```

Response:
```json
{
  "total_api_keys": 1,
  "total_users": 3,
  "revoked_tokens": 0,
  "jwt_expiration_hours": 24
}
```

---

## ✅ Phase 3 Checklist

- [x] JWT Token authentication
- [x] API Key authentication
- [x] Role-based access control
- [x] Login endpoint
- [x] User info endpoint
- [x] API key management (admin)
- [x] Auth statistics (admin)
- [x] Default users created
- [x] Default API key created
- [x] Prometheus metrics fixed
- [x] Documentation

---

## 🔜 Next Steps (Phase 4+)

| Phase | Focus | Items |
|-------|-------|-------|
| **Phase 4** | MLOps | MLflow, Model versioning |
| **Phase 5** | Clawdbot | Telegram/WhatsApp bot |
| **Phase 6** | Observability | OpenTelemetry, Jaeger |

---

## 👤 Author

**Sérgio Henrique**
- Email: sergio@lognullsec.com
- LinkedIn: [linkedin.com/in/akasergiosilva](https://linkedin.com/in/akasergiosilva)

---

**Phase 3 Complete** ✅ | Branch: `phase3-security`
