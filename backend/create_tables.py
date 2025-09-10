#!/usr/bin/env python3
"""
Script to create database tables for SimpleIQ backend
"""

# Import all models to ensure they're registered with SQLAlchemy
from app.database import create_tables

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")