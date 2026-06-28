#!/bin/bash
# Enterprise backup script for PostgreSQL, Redis, ChromaDB, and Documents

BACKUP_DIR="/backups/$(date +%Y-%m-%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Starting system backups to $BACKUP_DIR..."

# 1. Backup PostgreSQL
echo "Backing up PostgreSQL database..."
docker exec sales_postgres pg_dump -U postgres ai_sales_copilot > "$BACKUP_DIR/postgres_backup.sql"

# 2. Backup Redis
echo "Backing up Redis RDB dump..."
docker exec sales_redis redis-cli SAVE
docker cp sales_redis:/data/dump.rdb "$BACKUP_DIR/redis_backup.rdb"

# 3. Backup Knowledge Documents
echo "Backing up uploaded knowledge documents..."
tar -czf "$BACKUP_DIR/documents_backup.tar.gz" -C /app uploads/

# 4. Backup ChromaDB data dir
echo "Backing up ChromaDB persistent index..."
docker cp sales_chroma:/chroma/data "$BACKUP_DIR/chromadb_data"

echo "Backup complete! Files stored in $BACKUP_DIR"
