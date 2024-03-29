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


# обработчик всех исключений типа HTTPException
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc)},
    )


# обработчик ошибок синтаксиса в теле запроса - тип RequestValidationError ( Pydantic 422 Unprocessable Entity )
async def custom_request_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": "Custom Request Validation Error", "errors": exc.errors()},
    )


# обработчик исключений типа ValueError
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={'error': str(exc)}
    )
