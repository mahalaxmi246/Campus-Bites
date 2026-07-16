from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.canteen import CanteenResponse
from app.services.canteen_service import list_canteens

router = APIRouter()


@router.get("", response_model=list[CanteenResponse])
def list_all_canteens(db: Session = Depends(get_db)) -> list[CanteenResponse]:
    return list_canteens(db)