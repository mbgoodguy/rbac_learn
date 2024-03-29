from typing import Union

import uvicorn
from fastapi import HTTPException, FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, field_validator
from starlette.requests import Request
from starlette.responses import JSONResponse

from exceptions import CustomExceptionA, CustomExceptionB, CustomExceptionC, custom_exception_c_handler, \
    custom_http_exception_handler, custom_request_validation_exception_handler, value_error_handler

app = FastAPI()

# Обработчики исключений
app.add_exception_handler(CustomExceptionC, custom_exception_c_handler)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_request_validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)


# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=400,
#         content={"error": "Bad request"}
#     )

@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "error": exc.detail, 'info': exc.description}
    )


@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, 'description': exc.description}
    )


@app.get("/root")
async def main():
    res = 1 / 0  # сработает global_exception_handler если раскоментирован
    return {'msg': 'OK'}


@app.get("/items/{pk}")
async def check_custom_exc_a(pk: int):
    if pk == 1:
        raise CustomExceptionA()
    return {'msg': 'OK'}


@app.get("/items_2/{pk}")
async def check_custom_exc_b(pk: int):
    if pk == 2:
        raise CustomExceptionB()
    return {'msg': 'OK'}


@app.get("/items_3/{pk}")
async def check_custom_exc_c(pk: int):
    if pk == 3:
        raise CustomExceptionC()
    return {'msg': 'OK'}


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.post("/items/")
async def create_item(item: Item):

    # if item.price < 0:
    #     # сработает custom_http_exception_handler
    #     raise HTTPException(status_code=400, detail="Price must be non-negative")

    try:
        if item.price < 0:
            raise ValueError('Price must be non-negative')
    except ValueError as ve:
        raise ve  # сработает global_exception_handler если раскоментирован
    return {"message": "Item created successfully", "item": item}


if __name__ == '__main__':
    uvicorn.run('exceptions.main:app', reload=True)
