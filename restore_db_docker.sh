#!/bin/bash

# Set variables
DOCKER_CONTAINER="postgres"
DB_NAME="swotting"
DB_USER="swotting"

# Function to setup the database
setup_database() {
    echo "Setting up fresh database..."
    
    # Create role if it doesn't exist (will not error if role exists)
    docker exec "$DOCKER_CONTAINER" psql -U postgres -d postgres \
        -c "DO \$\$ BEGIN CREATE ROLE $DB_USER WITH LOGIN CREATEDB PASSWORD '$DB_USER'; EXCEPTION WHEN duplicate_object THEN RAISE NOTICE 'Role already exists'; END \$\$;"
    
    # Now use postgres user to create database and grant privileges
    docker exec "$DOCKER_CONTAINER" psql -U postgres -d postgres \
        -c "DROP DATABASE IF EXISTS $DB_NAME;" \
        -c "CREATE DATABASE $DB_NAME;" \
        -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    
    # Set ownership of the database to the swotting user
    docker exec "$DOCKER_CONTAINER" psql -U postgres -d postgres \
        -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"
}

# Function to restore from backup
restore_backup() {
    local DUMP_PATH="$1"
    local DUMP_FILE=$(basename "$DUMP_PATH")
    local TMP_PATH="/tmp"

    echo "Restoring from backup: $DUMP_FILE"
    
    # Check if the file exists within the /tmp directory in the container
    if ! docker exec -i "$DOCKER_CONTAINER" test -e "$TMP_PATH/$DUMP_FILE"; then
        # If it doesn't exist, copy it into /tmp within the Docker container
        docker cp "$DUMP_PATH" "$DOCKER_CONTAINER:$TMP_PATH"
    fi

    # Setup database first
    setup_database

    # Restore the database from the file using pg_restore
    docker exec -i "$DOCKER_CONTAINER" pg_restore -d "$DB_NAME" -c -U "$DB_USER" "$TMP_PATH/$DUMP_FILE"
}

# Main logic
if [ -z "$1" ]; then
    # No backup file provided, just setup the database
    setup_database
else
    # Backup file provided, restore from it
    restore_backup "$1"
fi

YELLOW='\033[1;33m'
NC='\033[0m' # No Color
echo -e "${YELLOW}Database operation completed successfully!${NC}"
