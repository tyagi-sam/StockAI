#!/usr/bin/env python3
"""
Database migration script for Stock AI application.
This script helps with database setup and migration management.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.logger import logger

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    print("\n🔍 Checking database connection...")
    try:
        from sqlalchemy import text
        from app.db.session import engine
        
        # Use sync engine for testing
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_migration(message):
    """Create a new migration"""
    return run_command(
        f"cd {backend_dir} && alembic revision --autogenerate -m '{message}'",
        f"Creating migration: {message}"
    )

def run_migrations():
    """Run all pending migrations"""
    return run_command(
        f"cd {backend_dir} && alembic upgrade head",
        "Running database migrations"
    )

def reset_database():
    """Reset the database (drop all tables and recreate)"""
    print("\n⚠️  WARNING: This will delete all data in the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Database reset cancelled")
        return False
    
    # Drop all tables
    if run_command(
        f"cd {backend_dir} && alembic downgrade base",
        "Dropping all tables"
    ):
        # Recreate tables
        return run_command(
            f"cd {backend_dir} && alembic upgrade head",
            "Recreating database tables"
        )
    return False

def show_migration_status():
    """Show current migration status"""
    return run_command(
        f"cd {backend_dir} && alembic current",
        "Checking migration status"
    )

def show_migration_history():
    """Show migration history"""
    return run_command(
        f"cd {backend_dir} && alembic history",
        "Showing migration history"
    )

def main():
    """Main function"""
    print("🚀 Stock AI Database Migration Tool")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python scripts/migrate.py <command> [options]")
        print("\nCommands:")
        print("  check     - Check database connection")
        print("  migrate   - Run all pending migrations")
        print("  create    - Create a new migration")
        print("  reset     - Reset database (drop all tables)")
        print("  status    - Show migration status")
        print("  history   - Show migration history")
        print("\nExamples:")
        print("  python scripts/migrate.py check")
        print("  python scripts/migrate.py migrate")
        print("  python scripts/migrate.py create 'Add user preferences'")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        check_database_connection()
    
    elif command == "migrate":
        if check_database_connection():
            run_migrations()
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Please provide a migration message")
            print("Example: python scripts/migrate.py create 'Add new table'")
            return
        message = sys.argv[2]
        create_migration(message)
    
    elif command == "reset":
        reset_database()
    
    elif command == "status":
        show_migration_status()
    
    elif command == "history":
        show_migration_history()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see available commands")

if __name__ == "__main__":
    main() 