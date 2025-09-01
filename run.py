import uvicorn
from app.db.init_db import create_tables, init_db
from app.db.base import SessionLocal

def setup_database():
    print("Setting up database...")
    create_tables()
    
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
    print("Starting server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
