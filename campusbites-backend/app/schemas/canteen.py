from pydantic import BaseModel, ConfigDict


class CanteenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str | None
    is_active: bool