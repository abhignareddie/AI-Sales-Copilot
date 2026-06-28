#!/bin/bash
# Enterprise restore script for PostgreSQL, Redis, ChromaDB, and Documents

if [ -z "$1" ]; then
  echo "Usage: ./restore.sh <path_to_backup_directory>"
  exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
  echo "Backup directory not found: $BACKUP_DIR"
  exit 1
fi

echo "Starting system restoration from $BACKUP_DIR..."

# 1. Restore PostgreSQL
if [ -f "$BACKUP_DIR/postgres_backup.sql" ]; then
  echo "Restoring PostgreSQL database..."
  cat "$BACKUP_DIR/postgres_backup.sql" | docker exec -i sales_postgres psql -U postgres -d ai_sales_copilot
fi

# 2. Restore Redis
if [ -f "$BACKUP_DIR/redis_backup.rdb" ]; then
  echo "Restoring Redis RDB dump..."
  docker cp "$BACKUP_DIR/redis_backup.rdb" sales_redis:/data/dump.rdb
  docker restart sales_redis
fi

# 3. Restore Knowledge Documents
if [ -f "$BACKUP_DIR/documents_backup.tar.gz" ]; then
  echo "Restoring uploaded knowledge documents..."
  tar -xzf "$BACKUP_DIR/documents_backup.tar.gz" -C /app
fi

# 4. Restore ChromaDB data
if [ -d "$BACKUP_DIR/chromadb_data" ]; then
  echo "Restoring ChromaDB persistent index..."
  docker cp "$BACKUP_DIR/chromadb_data" sales_chroma:/chroma/data
  docker restart sales_chroma
fi

echo "Restoration completed successfully!"
