from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    fish: str
    shaxs: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_atributes = True

class UserSignIn(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str