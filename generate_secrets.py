#!/usr/bin/env python3
"""
Production Secret Generator
===========================

SECURITY CRITICAL: Run this script to generate secure production secrets.

Usage:
    python generate_secrets.py

This will generate:
1. Cryptographically secure JWT secret key
2. Database password suggestions
3. Template for .env file

NEVER use the example values in production!
"""

import secrets
import string
import os
from urllib.parse import quote


def generate_jwt_secret(length=64):
    """Generate a cryptographically secure JWT secret key"""
    return secrets.token_hex(length)


def generate_password(length=32):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_database_url(db_name="ecom_production"):
    """Generate database URL template with secure password"""
    username = input("Enter database username: ").strip()
    if not username:
        username = "ecom_user"
    
    password = generate_password(24)
    host = input("Enter database host (default: localhost): ").strip() or "localhost"
    port = input("Enter database port (default: 5432): ").strip() or "5432"
    
    # URL encode the password to handle special characters
    encoded_password = quote(password)
    
    return f"postgresql://{username}:{encoded_password}@{host}:{port}/{db_name}", password


def main():
    print("🔐 Production Secret Generator")
    print("=" * 50)
    print("⚠️  CRITICAL: Use these secrets for production only!")
    print("⚠️  NEVER commit these to version control!")
    print("=" * 50)
    
    # Generate JWT secret
    jwt_secret = generate_jwt_secret()
    print(f"\n✅ JWT Secret Key (copy to SECRET_KEY):")
    print(f"   {jwt_secret}")
    
    # Generate database URL
    print(f"\n📊 Database Configuration:")
    db_url, db_password = generate_database_url()
    print(f"   Database URL: {db_url}")
    print(f"   Raw Password: {db_password}")
    
    # Generate webhook secret
    webhook_secret = generate_password(32)
    print(f"\n🔗 Stripe Webhook Secret (you'll get this from Stripe):")
    print(f"   Example format: whsec_{webhook_secret}")
    
    # Create .env template
    env_content = f"""# PRODUCTION ENVIRONMENT - GENERATED {os.getenv('USER', 'user')}
# ==============================================
# CRITICAL: Keep this file secure and private!
# ==============================================

# Database Configuration
DATABASE_URL={db_url}

# JWT Configuration - SECURE
SECRET_KEY={jwt_secret}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Configuration - ADD YOUR REAL KEYS
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_ACTUAL_STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY=sk_live_YOUR_ACTUAL_STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_ACTUAL_WEBHOOK_SECRET

# CORS Configuration - UPDATE WITH YOUR DOMAINS
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Environment
ENVIRONMENT=production
DEBUG=false
"""
    
    print(f"\n📝 Production .env Template:")
    print("=" * 50)
    print(env_content)
    print("=" * 50)
    
    # Offer to save
    save = input("\n💾 Save to .env.production? (y/N): ").strip().lower()
    if save == 'y':
        with open('.env.production', 'w') as f:
            f.write(env_content)
        print("✅ Saved to .env.production")
        print("⚠️  Remember to:")
        print("   1. Copy .env.production to .env")
        print("   2. Add your real Stripe keys")
        print("   3. Update CORS origins")
        print("   4. Set up your PostgreSQL database")
        print("   5. NEVER commit .env to git!")
    
    print("\n🔒 Security Checklist:")
    print("   ✅ Strong JWT secret generated")
    print("   ✅ Secure database password created")
    print("   ✅ .env template ready")
    print("   ⚠️  Add real Stripe production keys")
    print("   ⚠️  Configure production database")
    print("   ⚠️  Update CORS for your domain")
    print("   ⚠️  Verify .gitignore excludes .env")


if __name__ == "__main__":
    main()
