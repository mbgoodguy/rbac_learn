import logging

import uvicorn
from fastapi import FastAPI

from db.config import TodoTools
from pydantic_models import TodoPayload

# LOGGING
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')

# APP
app = FastAPI()


# ROUTES
@app.post('/todo')
async def create_todo(todo_data: TodoPayload):
    todo = TodoTools.add_todo(todo_data)

    # return {'msg': 'todo has been added'}
    return {'msg': f'Todo with id {todo.id} been added'}

# ENTRY POINT

if __name__ == '__main__':
    TodoTools.create_tables()
    uvicorn.run('main_2:app', reload=True)
