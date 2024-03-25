import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import TodoTable, Base
from pydantic_models import TodoPayload

dotenv_path = Path(__file__).parent.parent / '.env'

load_dotenv(dotenv_path=dotenv_path)


class DB_Settings:
    DB_USER = os.getenv('DB_USER')
    DB_HOST = os.getenv('DB_HOST')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    DB_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


settings = DB_Settings()
engine = create_engine(url=settings.DB_URL, echo=True)


class TodoTools:
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @classmethod
    def create_tables(cls):
        Base.metadata.create_all(engine)
        print(f'Таблицы созданы')

    @classmethod
    def add_todo(cls, todo_data: TodoPayload):
        todo = TodoTable(title=todo_data.title, description=todo_data.description, completed=todo_data.completed)

        with cls.session(autocommit=False, autoflush=False, bind=engine) as db:
            db.add(todo)
            db.commit()
            db.refresh(todo)

        return todo
