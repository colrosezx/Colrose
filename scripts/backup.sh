#!/bin/bash
# This script creates a timestamped backup of the PostgreSQL database using pg_dump.

# Stop script on errors
set -e

# --- Configuration ---
# Directory to store backups, relative to the script location
BACKUP_DIR_NAME="backups"
# Get the absolute path to the project root directory (one level up from the script's directory)
PROJECT_ROOT=$(dirname "$(dirname "$(realpath "$0")")")
BACKUP_DIR="$PROJECT_ROOT/$BACKUP_DIR_NAME"

# Create the backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Load environment variables from .env file in the project root
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | sed 's/#.*//g' | xargs)
else
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# --- Backup Execution ---
# Filename with timestamp, e.g., backup-2025-12-15_14-30-00.sql
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/backup-$TIMESTAMP.sql"

echo "Backing up database '$POSTGRES_DB' to $BACKUP_FILE..."

# Execute pg_dump inside the 'db' container.
# The '-T' flag disables pseudo-TTY, which is recommended for scripting.
# The command is executed from the project root to ensure docker compose finds its yml file.
(cd "$PROJECT_ROOT" && docker compose exec -T -e PGPASSWORD="$POSTGRES_PASSWORD" backend pg_dump -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB") > "$BACKUP_FILE"

echo "✅ Backup created successfully: $BACKUP_FILE"
