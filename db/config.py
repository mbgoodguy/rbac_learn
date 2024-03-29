import os
from contextlib import contextmanager
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

    DB_PSYCOPG2_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


settings = DB_Settings()
engine = create_engine(url=settings.DB_PSYCOPG2_URL, echo=True)


def db_session_method(method):
    def wrapper(cls, *args, **kwargs):
        with cls.get_db_session() as db:
            return method(cls, db, *args, **kwargs)
    return wrapper


class TodoTools:
    engine = create_engine(url=settings.DB_PSYCOPG2_URL, echo=True)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @classmethod
    def create_tables(cls):
        Base.metadata.create_all(cls.engine)
        print(f'Таблицы созданы')

    @classmethod
    @db_session_method
    def add_todo(cls, db, todo_data: TodoPayload):
        todo = TodoTable(title=todo_data.title, description=todo_data.description, completed=todo_data.completed)
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo

    @classmethod
    @db_session_method
    def get_all_todos(cls, db):
        return db.query(TodoTable).all()

    @classmethod
    @db_session_method
    def delete_todo_by_id(cls, db, pk: int):
        todo = db.get(TodoTable, pk)
        if todo:
            db.delete(todo)
            db.commit()
            return f'Todo with id {pk} deleted'
        else:
            raise Exception(f'Todo with id {pk} does not exist')

    @classmethod
    @db_session_method
    def update_todo(cls, db, pk: int, todo_data: TodoPayload):
        todo = db.get(TodoTable, pk)
        if todo:
            todo.title = todo_data.title
            todo.description = todo_data.description
            todo.completed = todo_data.completed
            db.add(todo)
            db.commit()
            return f'Todo with id {pk} updated'
        else:
            raise Exception(f'Todo with id {pk} does not exist')

    @classmethod
    @contextmanager
    def get_db_session(cls):
        db = cls.session()
        try:
            yield db
        finally:
            db.close()
