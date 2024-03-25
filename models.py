from enum import Enum

from pydantic import BaseModel, ConfigDict


class Role(Enum):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    role: Role


class AuthUser(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    role: Role


class UserInDB(User):
    hashed_password: str
