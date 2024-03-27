from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    name: str = Field(min_length=2, max_length=25)
    surname: str = Field(min_length=2, max_length=50)
    email: EmailStr()
    phone: str = Field(min_length=4, max_length=15)
    birthday: date = Field()
    notes: Optional[str] = Field(min_length=2, max_length=500)


class ContactUpdateSchema(ContactSchema):
    pass


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date
    notes: str
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    class Config:
        from_attributes = True
