from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """What the client SENDS to /auth/register."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    """What the server SENDS BACK. Notice: no password field at all."""
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}