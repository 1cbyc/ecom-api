#!/usr/bin/env bash
# Render.com build script

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "
from app.db.init_db import create_tables, init_db
from app.db.base import SessionLocal

print('🔧 Creating database tables...')
create_tables()

print('🔧 Initializing database with admin user...')
db = SessionLocal()
try:
    init_db(db)
    print('✅ Database initialization complete!')
except Exception as e:
    print(f'⚠️ Database initialization warning: {e}')
finally:
    db.close()
"
