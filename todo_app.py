import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.responses import Response, JSONResponse

from db.config import TodoTools
from pydantic_models import TodoPayload, Todo

# LOGGING
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')

# APP
app = FastAPI()


# @app.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    print(exc.errors())
    for error in exc.errors():
        errors.append(
            {
                "field": error["loc"][-1],
                "msg": error['msg'],
                "value": error["input"]
            }
        )

    return JSONResponse(status_code=400, content=errors)


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


todos = {"foo": "Listen to the Bar Fighters"}


@app.put("/get-or-create-todo/{pk}", status_code=200)
def get_or_create_todo(pk: int, todo_payload: TodoPayload, response: Response):
    todo = TodoTools.get_todo(pk=pk)
    if not todo:
        todo = TodoTools.add_todo(todo_payload)
        return todo
    return todo


@app.get("/todos-header/{pk}")
# async def read_todo_header(pk: int, x_error: Annotated[str | None, Header()] = None):
async def read_todo_header(pk: int, response: Response):
    todo = TodoTools.get_todo(pk)
    if todo:
        response.headers['User-Agent'] = 'ABOBA'
        return {'todo': todo}
    else:
        raise HTTPException(
            status_code=404,
            detail="ITEM NOT FOUND",
            headers={"X-Error": "There goes my error"},
        )


# ENTRY POINT
if __name__ == '__main__':
    TodoTools.create_tables()
    uvicorn.run('todo_app:app', reload=True)
