from pydantic import BaseModel, ConfigDict, Field


class MenuItemCreateRequest(BaseModel):
    canteen_id: int
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    price: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)


class MenuItemUpdateRequest(BaseModel):
    """All fields optional — PUT here behaves as a partial update.
    Only fields actually sent by the client get changed (see
    model_dump(exclude_unset=True) in the service)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    price: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    is_available: bool | None = None


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    canteen_id: int
    name: str
    description: str | None
    price: float
    category: str
    is_available: bool