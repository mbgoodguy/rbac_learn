from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from databases import Database
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# EXCEPTION HANDLERS


# URL для PostgreSQL
database = Database(settings.DB_URL)


# Модель User для валидации входных данных
class UserCreate(BaseModel):
    username: str
    email: str


# Модель User для валидации исходящих данных - чисто для демонстрации (обычно входная модель шире чем выходная, т.к.
# на вход мы просим, например, пароль, который обратно не возвращаем, и другое, что не обязательно возвращать)
class UserReturn(BaseModel):
    username: str
    email: str
    id: Optional[int] = None


@app.post('/users', response_model=UserReturn)
async def create_user(user: UserCreate):
    query = 'INSERT INTO users (username, email) VALUES (:username, :email) RETURNING id'
    values = {'username': user.username, 'email': user.email}
    try:
        user_id = await database.execute(query=query, values=values)
        return {**user.model_dump(), 'id': user_id}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='Failed to create user')


@app.get('/users', response_model=UserReturn)
async def get_user(user_id: int):
    query = 'SELECT * FROM users WHERE id = :user_id'
    values = {'user_id': user_id}
    # if user_id == 40:
    #     raise Exception('User with id 40 does not exist')

    try:
        result = await database.fetch_one(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to fetch user from db')

    if result:
        return UserReturn(username=result['username'], email=result['email'], id=result['id'])
    else:
        raise HTTPException(status_code=404, detail='User not found')


@app.put('/user/{user_id}', response_model=UserReturn)
async def update_user(user_id: int, user: UserCreate):
    query = 'UPDATE users SET username = :username, email = :email WHERE id = :user_id'
    values = {'user_id': user_id, 'username': user.username, 'email': user.email}

    try:
        await database.execute(query=query, values=values)
        return {**user.model_dump(), 'id': user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update user in database")


@app.delete('/user/{user_id}', response_model=UserReturn)
async def delete_user(user_id: int, user: UserCreate):
    query = "DELETE FROM users WHERE user_id= :user_id"
    values = {'user_id': user_id}

    try:
        deleted_rows = await database.execute(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete user in database")

    if deleted_rows:
        return {'message': "User deleted succesfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


if __name__ == '__main__':
    uvicorn.run('users_app:app', reload=True)
