import uvicorn
from fastapi import HTTPException, FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from exceptions import CustomExceptionA, CustomExceptionB, CustomExceptionC, custom_exception_c_handler

app = FastAPI()
app.add_exception_handler(CustomExceptionC, custom_exception_c_handler)


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
    res = 1 / 0  # здесь сработает global_exception_handler если раскоментирован
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


if __name__ == '__main__':
    uvicorn.run('exceptions.main:app', reload=True)
