"""Pydantic practice models."""
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class Address(BaseModel):
    street: str
    city: str
    zip_code: Annotated[str, Field(pattern=r"^\d{5}(-\d{4})?$")]


class User(BaseModel):
    id: int
    name: Annotated[str, Field(min_length=1, max_length=80)]
    email: EmailStr
    age: Annotated[int, Field(ge=0, le=130)]
    role: Literal["admin", "member", "guest"] = "member"
    signed_up: date | None = None
    address: Address | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def admins_need_address(self):
        if self.role == "admin" and self.address is None:
            raise ValueError("admins must have an address")
        return self
