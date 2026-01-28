#!/bin/bash

# =============================================================================
# 🏗️ Transaction Guardian v2.0 - Phase 1 Setup
# =============================================================================
# Este script configura toda a infraestrutura da Fase 1 (TimescaleDB)
#
# Uso:
#   chmod +x setup_phase1.sh
#   ./setup_phase1.sh
# =============================================================================

set -e

echo "🏗️ Transaction Guardian v2.0 - Phase 1 Setup"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# 1. Verificar Docker
# -----------------------------------------------------------------------------
echo "🐳 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi
echo "   ✅ Docker is installed"

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running. Please start Docker."
    exit 1
fi
echo "   ✅ Docker daemon is running"
echo ""

# -----------------------------------------------------------------------------
# 2. Criar diretórios
# -----------------------------------------------------------------------------
echo "📁 Creating directories..."
mkdir -p infrastructure/timescaledb/init
echo "   ✅ Directories created"
echo ""

# -----------------------------------------------------------------------------
# 3. Criar rede Docker
# -----------------------------------------------------------------------------
echo "🌐 Creating Docker network..."
docker network create monitoring 2>/dev/null && echo "   ✅ Network 'monitoring' created" || echo "   ⏭️  Network 'monitoring' already exists"
echo ""

# -----------------------------------------------------------------------------
# 4. Subir TimescaleDB
# -----------------------------------------------------------------------------
echo "🐘 Starting TimescaleDB..."
docker compose -f infrastructure/docker-compose.timescale.yml up -d

echo "   ⏳ Waiting for database to be ready..."
sleep 5

# Aguardar o banco ficar pronto
for i in {1..30}; do
    if docker exec guardian-timescaledb pg_isready -U guardian -d transaction_guardian &>/dev/null; then
        echo "   ✅ TimescaleDB is ready!"
        break
    fi
    echo "   ⏳ Waiting... ($i/30)"
    sleep 2
done
echo ""

# -----------------------------------------------------------------------------
# 5. Verificar schema
# -----------------------------------------------------------------------------
echo "📊 Verifying schema..."
TABLES=$(docker exec guardian-timescaledb psql -U guardian -d transaction_guardian -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
echo "   ✅ $TABLES tables created"
echo ""

# -----------------------------------------------------------------------------
# 6. Instalar dependências Python
# -----------------------------------------------------------------------------
echo "🐍 Installing Python dependencies..."
if [ -f "code/requirements-phase1.txt" ]; then
    pip install -r code/requirements-phase1.txt --quiet
    echo "   ✅ Python dependencies installed"
else
    echo "   ⚠️  requirements-phase1.txt not found, skipping"
fi
echo ""

# -----------------------------------------------------------------------------
# 7. Testar conexão
# -----------------------------------------------------------------------------
echo "🔌 Testing database connection..."
if docker exec guardian-timescaledb psql -U guardian -d transaction_guardian -c "SELECT 1" &>/dev/null; then
    echo "   ✅ Connection successful!"
else
    echo "   ❌ Connection failed"
    exit 1
fi
echo ""

# -----------------------------------------------------------------------------
# Done!
# -----------------------------------------------------------------------------
echo "=============================================="
echo "🎉 Phase 1 Setup Complete!"
echo ""
echo "📊 Services running:"
echo "   • TimescaleDB: localhost:5432"
echo "   • pgAdmin: http://localhost:5050"
echo ""
echo "🔑 Credentials:"
echo "   • Database: guardian / guardian_secure_2024"
echo "   • pgAdmin: admin@guardian.local / admin"
echo ""
echo "📋 Next steps:"
echo "   1. Migrate existing data:"
echo "      python code/migrate_csv_to_timescale.py --csv-path data/transactions.csv"
echo ""
echo "   2. Test the connection:"
echo "      python code/database.py"
echo ""
echo "   3. Connect via psql:"
echo "      docker exec -it guardian-timescaledb psql -U guardian -d transaction_guardian"
echo "=============================================="
