#!/bin/bash
# reset_and_restore_db.sh

# Database configuration from your .env
DB_USER="swotting"
DB_NAME="swotting"
DB_PASSWORD="swotting"
DB_HOST="127.0.0.1"

# Check if dump file is provided
DUMP_FILE=$1
RESTORE_MODE=false

if [ ! -z "$DUMP_FILE" ]; then
    if [ ! -f "$DUMP_FILE" ]; then
        echo "Error: Dump file not found at $DUMP_FILE"
        exit 1
    fi
    RESTORE_MODE=true
fi

echo "🗑️  Dropping existing database and user..."
PGPASSWORD="postgres" psql -U postgres -h $DB_HOST << EOF
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;
EOF

echo "🔨 Creating new database and user..."
PGPASSWORD="postgres" psql -U postgres -h $DB_HOST << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\c $DB_NAME
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
GRANT USAGE ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
ALTER USER $DB_USER SUPERUSER;
ALTER SCHEMA public OWNER TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $DB_USER;
EOF

if [ "$RESTORE_MODE" = true ]; then
    echo "📥 Restoring from dump..."
    PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME --no-owner --no-privileges --clean --if-exists "$DUMP_FILE"

    if [ $? -eq 0 ]; then
        echo "✅ Database reset and restore completed successfully!"
    else
        echo "⚠️  Warning: pg_restore completed with some warnings or errors."
        echo "This is often normal if the dump contains CREATE/DROP statements."
    fi
else
    echo "✅ Clean database created successfully with all required permissions!"
fi