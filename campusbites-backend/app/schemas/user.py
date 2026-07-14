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