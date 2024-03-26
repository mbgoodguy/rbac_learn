import uvicorn
from fastapi import FastAPI

from db.config import TodoTools
from pydantic_models import TodoPayload, Todo

# LOGGING
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')

# APP
app = FastAPI()


# ROUTES
@app.post('/todo', response_model=Todo)
async def create_todo(todo_data: TodoPayload):
    todo = TodoTools.add_todo(todo_data)

    # return {'msg': 'todo has been added'}
    # return {'msg': f'Todo with id {todo.id} been added'}
    return todo


@app.get('/todo_list')
async def get_all_todo():
    todo = TodoTools.get_all_todos()

    return todo


@app.get('/delete')
async def delete_todo(pk: int):
    todo = TodoTools.delete_todo_by_id(pk)

    return todo


@app.put('/update')
async def update_todo(pk: int, todo_data: TodoPayload):
    todo = TodoTools.update_todo(pk, todo_data)

    return todo


# ENTRY POINT
if __name__ == '__main__':
    TodoTools.create_tables()
    uvicorn.run('main_2:app', reload=True)
