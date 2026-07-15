from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import UserRole


class UserRegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # 72 = bcrypt's hard limit


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    username: str
    email: str
    role: UserRole

class StaffCreateRequest(UserRegisterRequest):
    """
    Same shape as UserRegisterRequest today, but kept as a distinct schema
    on purpose — this is an admin-provisioning action, not self-registration,
    and the two may need to diverge later (e.g. assigning a canteen to
    staff in Phase 3) without touching public registration's contract.
    """

    pass