# 🛒 E-Commerce API

A production-ready e-commerce API built with FastAPI, featuring JWT authentication, Stripe payments, and comprehensive order management.

## 🚀 Features

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Product Management**: Full CRUD operations with categories and search
- **Shopping Cart**: Persistent cart with real-time inventory validation
- **Payment Processing**: Stripe integration with webhooks
- **Order Management**: Complete order lifecycle with status tracking
- **Admin Panel**: Administrative endpoints for order and product management

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (dev) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Authentication**: JWT with bcrypt password hashing
- **Payments**: Stripe API
- **Validation**: Pydantic
- **Documentation**: Auto-generated OpenAPI/Swagger

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user profile

### Products
- `GET /api/v1/products/` - List products with filtering
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/` - Create product (Admin)

### Shopping Cart
- `GET /api/v1/cart/` - Get user's cart
- `POST /api/v1/cart/add` - Add item to cart
- `PUT /api/v1/cart/items/{product_id}` - Update quantity

### Checkout & Payments
- `POST /api/v1/checkout/create-payment-intent` - Create Stripe payment
- `POST /api/v1/checkout/webhook` - Stripe webhook handler

### Orders
- `GET /api/v1/orders/my-orders` - User's order history
- `GET /api/v1/orders/admin/all` - All orders (Admin)

## 🔧 Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./ecom.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Admin Account
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-admin-password

# Production Settings
DEBUG=False
ENVIRONMENT=production
```

## 🚀 Deployment

This API is configured for deployment on [Render.com](https://render.com):

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically from the `deploy-to-render` branch

## 📖 Documentation

Once deployed, visit `/docs` for interactive API documentation powered by Swagger UI.

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- Environment variable configuration
- Input validation with Pydantic
- CORS configuration
- SQL injection protection via SQLAlchemy ORM

## 🛡️ Production Ready

- Comprehensive error handling
- Request/response validation
- Database migrations support
- Logging configuration
- Health check endpoints
- Webhook security verification