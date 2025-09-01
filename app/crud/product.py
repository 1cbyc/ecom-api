from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from typing import Optional, List, Tuple
from math import ceil
from app.models.product import Product, Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductSearch, CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    return db.query(Category).filter(Category.slug == slug).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Category]:
    query = db.query(Category)
    if active_only:
        query = query.filter(Category.is_active == True)
    return query.offset(skip).limit(limit).all()


def create_category(db: Session, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    db_category.is_active = False
    db.commit()
    return True


def get_product(db: Session, product_id: int, active_only: bool = True) -> Optional[Product]:
    query = db.query(Product).options(joinedload(Product.categories))
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.filter(Product.id == product_id).first()


def get_product_by_slug(db: Session, slug: str, active_only: bool = True) -> Optional[Product]:
    query = db.query(Product).options(joinedload(Product.categories))
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.filter(Product.slug == slug).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    return db.query(Product).filter(Product.sku == sku).first()


def search_products(db: Session, search_params: ProductSearch) -> Tuple[List[Product], int]:
    query = db.query(Product).options(joinedload(Product.categories))
    
    # Always filter active products for public search
    query = query.filter(Product.is_active == True)
    
    # Search by name or description
    if search_params.search:
        search_term = f"%{search_params.search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.short_description.ilike(search_term)
            )
        )
    
    # Filter by category
    if search_params.category_id:
        query = query.join(Product.categories).filter(Category.id == search_params.category_id)
    
    # Filter by price range
    if search_params.min_price is not None:
        query = query.filter(Product.price >= search_params.min_price)
    if search_params.max_price is not None:
        query = query.filter(Product.price <= search_params.max_price)
    
    # Filter by featured
    if search_params.is_featured is not None:
        query = query.filter(Product.is_featured == search_params.is_featured)
    
    # Filter by stock availability
    if search_params.in_stock_only:
        query = query.filter(
            or_(
                Product.track_inventory == False,
                and_(
                    Product.track_inventory == True,
                    or_(
                        Product.inventory_quantity > 0,
                        Product.allow_backorders == True
                    )
                )
            )
        )
    
    # Count total results before pagination
    total = query.count()
    
    # Apply sorting
    if search_params.sort_by == "name":
        order_col = Product.name
    elif search_params.sort_by == "price":
        order_col = Product.price
    else:  # created_at
        order_col = Product.created_at
    
    if search_params.sort_order == "asc":
        query = query.order_by(asc(order_col))
    else:
        query = query.order_by(desc(order_col))
    
    # Apply pagination
    offset = (search_params.page - 1) * search_params.limit
    products = query.offset(offset).limit(search_params.limit).all()
    
    return products, total


def create_product(db: Session, product: ProductCreate) -> Product:
    # Create product without categories first
    product_data = product.model_dump(exclude={'category_ids'})
    db_product = Product(**product_data)
    
    # Add categories if provided
    if product.category_ids:
        categories = db.query(Category).filter(Category.id.in_(product.category_ids)).all()
        db_product.categories = categories
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    db_product = get_product(db, product_id, active_only=False)
    if not db_product:
        return None
    
    update_data = product_update.model_dump(exclude_unset=True, exclude={'category_ids'})
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    # Update categories if provided
    if product_update.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(product_update.category_ids)).all()
        db_product.categories = categories
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id, active_only=False)
    if not db_product:
        return False
    
    db_product.is_active = False
    db.commit()
    return True


def get_featured_products(db: Session, limit: int = 10) -> List[Product]:
    return db.query(Product).options(joinedload(Product.categories)).filter(
        and_(Product.is_active == True, Product.is_featured == True)
    ).limit(limit).all()


def update_product_inventory(db: Session, product_id: int, quantity_change: int) -> Optional[Product]:
    db_product = get_product(db, product_id, active_only=False)
    if not db_product:
        return None
    
    if db_product.track_inventory:
        new_quantity = db_product.inventory_quantity + quantity_change
        if new_quantity < 0:
            new_quantity = 0
        db_product.inventory_quantity = new_quantity
        db.commit()
        db.refresh(db_product)
    
    return db_product
