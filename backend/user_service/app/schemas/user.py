
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class UserProfileCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None


class UserProfileResponse(BaseModel):
    id: int
    auth_user_id: int
    first_name: str
    last_name: str
    phone_number: str | None
    date_of_birth: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
