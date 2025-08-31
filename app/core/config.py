"""
Core configuration settings for the e-commerce API.

This module handles all environment variables and application settings.
Using Pydantic for settings provides automatic validation and type checking.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Pydantic automatically validates types and can load from:
    - Environment variables
    - .env files
    - Default values defined here
    """
    
    # Project Information
    PROJECT_NAME: str = "E-commerce API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A comprehensive e-commerce API with authentication, payments, and admin features"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/ecom_db"
    
    # Security
    SECRET_KEY: str = "change-this-super-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Stripe Payment Gateway
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # CORS (Cross-Origin Resource Sharing) - for frontend integration
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5500"]
    
    class Config:
        """
        Pydantic configuration.
        env_file tells Pydantic to look for a .env file to load settings.
        """
        env_file = ".env"
        case_sensitive = True


# Create a global settings instance
# This will be imported throughout the application
settings = Settings()
