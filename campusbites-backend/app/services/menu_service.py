from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Canteen, MenuItem
from app.schemas.menu import MenuItemCreateRequest, MenuItemUpdateRequest


def create_menu_item(db: Session, data: MenuItemCreateRequest) -> MenuItem:
    canteen = db.query(Canteen).filter(Canteen.id == data.canteen_id).first()
    if canteen is None:
        raise AppError(
            code="CANTEEN_NOT_FOUND", message="Canteen does not exist", status_code=404
        )

    item = MenuItem(
        canteen_id=data.canteen_id,
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_menu_item_or_404(db: Session, item_id: int) -> MenuItem:
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if item is None:
        raise AppError(
            code="MENU_ITEM_NOT_FOUND", message="Menu item not found", status_code=404
        )
    return item


def update_menu_item(db: Session, item_id: int, data: MenuItemUpdateRequest) -> MenuItem:
    item = get_menu_item_or_404(db, item_id)

    # exclude_unset, not exclude_none: a client explicitly sending
    # description=null should clear it, but a field they never mentioned
    # at all must be left untouched. Those are different intents.
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_menu_item(db: Session, item_id: int) -> None:
    """
    Soft delete: mark unavailable rather than hard-deleting. Once real
    orders exist referencing this item (Week 5+), a hard delete would
    violate the order_items -> menu_items foreign key — and even ignoring
    that, order_items already snapshots name/price at order time
    specifically so history stays correct regardless of what happens to
    the live menu item afterward.
    """
    item = get_menu_item_or_404(db, item_id)
    item.is_available = False
    db.commit()

def list_menu_items(
    db: Session,
    canteen_id: int | None = None,
    category: str | None = None,
    include_unavailable: bool = False,
) -> list[MenuItem]:
    """
    Public browse endpoint's query. Defaults to available items only —
    that's the customer-facing "what can I actually order right now" view.
    include_unavailable=True is for the staff "manage menu" page (Week 3,
    Day 5), which needs to see 86'd/discontinued items too so staff can
    toggle them back on. Not role-gated: menu items carry no sensitive
    data, so there's no real harm in anyone passing this flag — keeping
    the route simple and fully public, matching the Day 1 API contract.
    """
    query = db.query(MenuItem)
    if canteen_id is not None:
        query = query.filter(MenuItem.canteen_id == canteen_id)
    if category is not None:
        query = query.filter(MenuItem.category == category)
    if not include_unavailable:
        query = query.filter(MenuItem.is_available.is_(True))
    return query.order_by(MenuItem.category, MenuItem.name).all()