"""
Shopping cart business logic.

All functions are scoped to a specific user_id — there is no such thing
as viewing or modifying another user's cart, enforced here rather than
left to the route layer to remember.
"""

from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.db.models import CartItem, Product
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemOut, CartOut


class ProductNotFoundError(Exception):
    pass


class ProductInactiveError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class CartItemNotFoundError(Exception):
    pass


def _to_cart_out(cart_items: list[CartItem]) -> CartOut:
    items_out: list[CartItemOut] = []
    subtotal = Decimal("0.00")
    for ci in cart_items:
        line_total = ci.product.price * ci.quantity
        subtotal += line_total
        items_out.append(
            CartItemOut(
                id=ci.id,
                product_id=ci.product_id,
                product_name=ci.product.name,
                unit_price=ci.product.price,
                quantity=ci.quantity,
                line_total=line_total,
                image_url=ci.product.image_url,
                in_stock=ci.product.is_active and ci.product.stock_quantity >= ci.quantity,
            )
        )
    return CartOut(items=items_out, subtotal=subtotal, item_count=sum(i.quantity for i in cart_items))


def get_cart(db: Session, user_id: int) -> CartOut:
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == user_id)
        .order_by(CartItem.created_at)
        .all()
    )
    return _to_cart_out(cart_items)


def add_item(db: Session, user_id: int, payload: CartItemCreate) -> CartOut:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise ProductNotFoundError()
    if not product.is_active:
        raise ProductInactiveError()

    existing = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == payload.product_id)
        .first()
    )
    new_quantity = (existing.quantity if existing else 0) + payload.quantity

    if new_quantity > product.stock_quantity:
        raise InsufficientStockError()

    if existing:
        existing.quantity = new_quantity
    else:
        db.add(CartItem(user_id=user_id, product_id=payload.product_id, quantity=payload.quantity))

    db.commit()
    return get_cart(db, user_id)


def update_item(db: Session, user_id: int, cart_item_id: int, payload: CartItemUpdate) -> CartOut:
    item = (
        db.query(CartItem)
        .filter(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        .first()
    )
    if item is None:
        raise CartItemNotFoundError()

    product = db.get(Product, item.product_id)
    if payload.quantity > product.stock_quantity:
        raise InsufficientStockError()

    item.quantity = payload.quantity
    db.commit()
    return get_cart(db, user_id)


def remove_item(db: Session, user_id: int, cart_item_id: int) -> CartOut:
    item = (
        db.query(CartItem)
        .filter(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        .first()
    )
    if item is None:
        raise CartItemNotFoundError()

    db.delete(item)
    db.commit()
    return get_cart(db, user_id)
