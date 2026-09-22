"""Category business logic."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Category, Product
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryNameTakenError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class CategoryHasProductsError(Exception):
    pass


def list_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


def get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise CategoryNotFoundError()
    return category


def create_category(db: Session, payload: CategoryCreate) -> Category:
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CategoryNameTakenError()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CategoryNameTakenError()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    has_products = db.query(Product).filter(Product.category_id == category_id).first() is not None
    if has_products:
        raise CategoryHasProductsError()
    db.delete(category)
    db.commit()
