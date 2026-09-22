"""Product business logic: listing/search, detail lookup, and admin CRUD."""

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.db.models import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductNotFoundError(Exception):
    pass


def list_products(
    db: Session,
    *,
    search: str | None = None,
    category_id: int | None = None,
    active_only: bool = True,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Product], int]:
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active.is_(True))
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Product.name.ilike(like), Product.description.ilike(like)))

    total = query.count()
    items = (
        query.order_by(Product.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_product(db: Session, product_id: int) -> Product:
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id == product_id)
        .first()
    )
    if product is None:
        raise ProductNotFoundError()
    return product


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return get_product(db, product.id)  # reload with category joined


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise ProductNotFoundError()
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return get_product(db, product.id)


def delete_product(db: Session, product_id: int) -> None:
    product = db.get(Product, product_id)
    if product is None:
        raise ProductNotFoundError()
    # Soft delete: products referenced by historical order_items cannot be
    # hard-deleted (ON DELETE RESTRICT), and hiding rather than removing
    # also preserves it for order history display. Admin "delete" means
    # "stop selling this", not "erase the record".
    product.is_active = False
    db.commit()
