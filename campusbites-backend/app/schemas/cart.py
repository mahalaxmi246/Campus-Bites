from pydantic import BaseModel, Field


class CartItemInput(BaseModel):
    """
    Note there is deliberately NO price field here. The client can only
    ever say "I want N of item X" — it structurally cannot submit a price,
    because there's nowhere to put one. Pricing always comes from the DB.
    """

    menu_item_id: int
    quantity: int = Field(gt=0, le=50)  # sane upper bound against garbage/malicious quantities


class ValidatedCartItem(BaseModel):
    menu_item_id: int
    name: str
    price: float  # the CURRENT live price from the DB, never client-supplied
    quantity: int
    line_subtotal: float


class CartValidationResult(BaseModel):
    items: list[ValidatedCartItem]
    subtotal: float
    handling_fee: float
    total: float