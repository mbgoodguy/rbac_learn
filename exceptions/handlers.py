from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponseModel(BaseModel):
    status_code: str
    detail: str
    description: str
    additional: str


def custom_exception_c_handler(request: Request, exc: Exception | ErrorResponseModel):
    print("Произошла ошибка. Нужно проверить лог")
    return JSONResponse(
        content={
            "status_code": int(exc.status_code),
            "detail": exc.detail,
            "description": exc.description,
            "additional": exc.additional,
        },
    )
