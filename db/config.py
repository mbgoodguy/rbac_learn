import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import TodoTable, Base
from exceptions import raise_not_exist
from pydantic_models import TodoPayload, Todo

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

    # CRUD methods
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
        print(f'TYPE OF todo var: {type(todo)}')
        return todo

    @classmethod
    def get_all_todos(cls):
        with cls.session(autocommit=False, autoflush=False, bind=engine) as db:
            res = db.query(TodoTable).all()

            return res

    @classmethod
    def delete_todo_by_id(cls, pk: int):
        with cls.session(autocommit=False, autoflush=False, bind=engine) as db:
            todo = db.get(TodoTable, pk)

            if todo:
                db.delete(todo)
                db.commit()
                # return todo
                return f'Todo with id {pk} deleted'
            else:
                raise_not_exist(pk)

    @classmethod
    def update_todo(cls, pk: int, todo_data: TodoPayload):
        with cls.session(autocommit=False, autoflush=False, bind=engine) as db:
            todo = db.get(TodoTable, pk)
            print(todo)

            if todo:
                todo.title = todo_data.title
                todo.description = todo_data.description
                todo.completed = todo_data.completed

                db.add(todo)
                db.commit()
                return f'Todo with id {pk} updated'
            else:
                raise_not_exist(pk)
