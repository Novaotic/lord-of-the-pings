#!/usr/bin/env python3
"""
Database migration script for Lord of the Pings.

This script handles database schema migrations and data migrations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from db.models import Base
from db.init_db import DB_URL

def create_tables():
    """Create all database tables."""
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    print("✓ All tables created successfully")

def drop_tables():
    """Drop all database tables (use with caution)."""
    engine = create_engine(DB_URL)
    Base.metadata.drop_all(engine)
    print("✓ All tables dropped successfully")

def migrate():
    """Run database migrations."""
    print("Running database migrations...")
    
    # Create tables if they don't exist
    create_tables()
    
    # Add any data migrations here
    # For example, adding default settings or initial data
    
    print("✓ Migrations completed successfully")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument("action", choices=["create", "drop", "migrate"], 
                       help="Action to perform: create tables, drop tables, or migrate")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_tables()
    elif args.action == "drop":
        drop_tables()
    elif args.action == "migrate":
        migrate()
