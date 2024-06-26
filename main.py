# module for RBAC app
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from exceptions import incorrect_access_rights, inactive_exc

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": 'admin'
    },
    "user1": {
        "username": "user1",
        "full_name": "just user",
        "email": "user1@example.com",
        "hashed_password": "$2b$12$yI5K0k6rxJAtRd2FgR5eOu/IcA0E0kDGbIYy3Zkuq8binQoGlzGQm",
        "disabled": False,
        "role": 'user'
    },
    "guest": {
        "username": "guest",
        "full_name": "just guest",
        "email": "guest@example.com",
        "hashed_password": "$2b$12$fiRsDmxzfFQb39LwgOSN5ufMV7r6ItraxMghijykLVMr.fo9xSOQS",
        "disabled": False,
        "role": 'guest'
    }

}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Role(Enum):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    role: Role


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def get_user(username: str) -> UserInDB:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user_from_token)]):
    if current_user.disabled:
        raise inactive_exc
    return current_user


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/info", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


# Защищенный роут только для админов, когда токен уже получен
@app.get("/admin")
def get_admin_info(current_user: str = Depends(get_current_user_from_token)):
    user_data = get_user(current_user.username)
    # print(user_data)
    # print(type(user_data))
    if user_data.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not correct access rights")
    return {"message": "Welcome Admin!"}


# роут только для юзеров, когда токен получен
@app.get("/user")
def get_user_info(current_user: str = Depends(get_current_user_from_token)):
    user_data = get_user(current_user.username)
    # print(user_data)
    # print(type(user_data))
    if user_data.role.value != "user":
        raise incorrect_access_rights
    return {"message": "Welcome User!"}


# роут для юзеров и админов когда токен получен
@app.get('/protected_resource')
def get_protected_resource(current_user: str = Depends(get_current_user_from_token)):
    user_data = get_user(current_user.username)
    if user_data.role.value not in [Role.ADMIN.value, Role.USER.value]:
        raise incorrect_access_rights
    return {"message": "Welcome to protected resource!"}


# роут для авторизованных пользователей
@app.get('/resource_for_authorized')
def get_resource_for_authorized(current_user: str = Depends(get_current_user_from_token)):
    user_data = get_user(current_user.username)
    if user_data.role.value in [Role.ADMIN.value, Role.USER.value, Role.GUEST.value]:
        return {"message": "Welcome to resource for authorized users!"}
    else:
        raise incorrect_access_rights


# роут для всех, включая неавторизованных
@app.get('/unprotected_resource')
def get_unprotected_resource():
    return {"message": "Welcome!"}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
