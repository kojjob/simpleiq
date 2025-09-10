#!/usr/bin/env python3
"""
Test script to create database tables and identify schema issues
"""

import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base
from app.models.user import User
from app.models.data_source import DataSource
from app.models.dataset import Dataset
from app.models.data_processing_job import DataProcessingJob

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/simpleiq"

async def create_tables():
    print("Creating async engine...")
    engine = create_async_engine(DATABASE_URL)
    
    try:
        print("Creating tables...")
        async with engine.begin() as conn:
            # First drop all tables if they exist
            await conn.run_sync(Base.metadata.drop_all)
            print("Dropped existing tables")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("Created all tables successfully!")
            
            # Inspect the data_sources table
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'data_sources' 
                ORDER BY ordinal_position
            """))
            
            print("\ndata_sources table schema:")
            for row in result:
                print(f"  {row[0]}: {row[1]} {'NULL' if row[2] == 'YES' else 'NOT NULL'}")
                
            # Inspect the datasets table foreign keys
            result = await conn.execute(text("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='datasets'
            """))
            
            print("\ndatasets table foreign keys:")
            for row in result:
                print(f"  {row[0]}: {row[1]}.{row[2]} -> {row[3]}.{row[4]}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())