from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    PROJECT_NAME: str = "E-commerce API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production E-commerce API with auth, payments, and admin"
    
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # CRITICAL: All sensitive data MUST come from environment variables
    DATABASE_URL: str
    
    # JWT Configuration - NEVER hardcode these
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Stripe Configuration - Production keys
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # CORS origins - restrict in production
    BACKEND_CORS_ORIGINS: list = []
    
    # Admin credentials - CRITICAL for initial setup
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str
    
    # Environment
    ENVIRONMENT: str = "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# to create a global settings instance
# will be imported throughout the app
settings = Settings()
