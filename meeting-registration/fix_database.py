#!/usr/bin/env python
"""Fix database structure"""

import os
os.environ['FLASK_ENV'] = 'development'

from sqlalchemy import create_engine, text
from config import config

def fix_database():
    """Add missing columns and create new tables"""
    
    # Get database URL
    db_config = config['development']
    engine = create_engine(db_config.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as conn:
        print("🔧 Fixing database structure...")
        
        # Start transaction
        trans = conn.begin()
        
        try:
            # 1. Add missing columns to meetings
            print("Adding columns to meetings table...")
            conn.execute(text("""
                ALTER TABLE meetings 
                ADD COLUMN IF NOT EXISTS organizer_id INTEGER,
                ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT TRUE
            """))
            
            # 2. Create users table
            print("Creating users table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """))
            
            # 3. Create otp_tokens table
            print("Creating otp_tokens table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS otp_tokens (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    token VARCHAR(6) NOT NULL,
                    purpose VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    used BOOLEAN DEFAULT FALSE
                )
            """))
            
            # 4. Add foreign key
            print("Adding foreign key constraint...")
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'fk_meetings_organizer'
                    ) THEN
                        ALTER TABLE meetings
                        ADD CONSTRAINT fk_meetings_organizer 
                        FOREIGN KEY (organizer_id) 
                        REFERENCES users(id)
                        ON DELETE SET NULL;
                    END IF;
                END $$;
            """))
            
            # 5. Add index
            print("Adding indexes...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_otp_email ON otp_tokens(email)
            """))
            
            # Commit transaction
            trans.commit()
            print("✅ Database structure fixed successfully!")
            
            # Verify
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            print(f"\n📊 Tables in database: {tables}")
            
            # Check data
            for table in ['employees', 'meetings', 'registrations']:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  - {table}: {count} rows")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    fix_database()