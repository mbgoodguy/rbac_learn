from fastapi import HTTPException
from starlette import status

unauthed_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Invalid username or password'
)

inactive_exc = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='User inactive'
)

incorrect_access_rights = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not correct access rights"
)
