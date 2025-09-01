import os
from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine
from app.models import User, UserRole
from app.crud.user import create_admin_user, get_user_by_email
from app.schemas.user import UserCreate
from app.db.base import Base


def init_db(db: Session) -> None:
    # SECURITY: Admin credentials from environment variables
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_password:
        print("⚠️  WARNING: ADMIN_PASSWORD not set in environment!")
        print("   Set ADMIN_PASSWORD in your .env file for production")
        admin_password = "CHANGE_THIS_ADMIN_PASSWORD_IMMEDIATELY"
    
    admin_user = get_user_by_email(db, email=admin_email)
    
    if not admin_user:
        admin_user_in = UserCreate(
            email=admin_email,
            username="admin",
            password=admin_password,
            full_name="System Administrator"
        )
        admin_user = create_admin_user(db, user=admin_user_in)
        print(f"✅ Admin user created: {admin_user.email}")
        if admin_password == "CHANGE_THIS_ADMIN_PASSWORD_IMMEDIATELY":
            print("🚨 SECURITY WARNING: Change admin password immediately!")
    else:
        print("ℹ️  Admin user already exists")


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created")


if __name__ == "__main__":
    create_tables()
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
