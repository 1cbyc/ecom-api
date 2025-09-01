from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import auth, products, categories, cart, checkout, orders
from app.db.init_db import create_tables, init_db
from app.db.base import SessionLocal

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
app.include_router(cart.router, prefix=f"{settings.API_V1_STR}/cart", tags=["shopping-cart"])
app.include_router(checkout.router, prefix=f"{settings.API_V1_STR}/checkout", tags=["checkout-payment"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["order-management"])


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and admin user on startup"""
    print("🚀 Starting up E-commerce API...")
    
    # Create database tables
    create_tables()
    print("✅ Database tables created")
    
    # Initialize admin user
    db = SessionLocal()
    try:
        init_db(db)
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
    finally:
        db.close()
    
    print("🎉 E-commerce API startup complete!")


@app.get("/")
def read_root():
    return {"message": "E-commerce API", "version": settings.VERSION}
