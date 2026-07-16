from sqlalchemy.orm import Session

from app.models import Canteen


def list_canteens(db: Session) -> list[Canteen]:
    return db.query(Canteen).filter(Canteen.is_active.is_(True)).order_by(Canteen.name).all()