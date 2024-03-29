from fastapi import HTTPException


class CustomExceptionA(HTTPException):
    def __init__(self,
                 status_code=404,
                 detail='Method not allowed',
                 description='your browser has sent an HTTP request (GET, POST, PUT, etc.) that isnt allowed for that resource'):
        super().__init__(status_code=status_code, detail=detail)
        self.description = description


class CustomExceptionB(HTTPException):
    def __init__(self,
                 status_code=500,
                 detail='Internal Server error',
                 description='Your request raised server error. Dont do requests like that'):
        super().__init__(status_code=status_code, detail=detail)
        self.description = description


class CustomExceptionC(HTTPException):
    def __init__(self,
                 status_code=400,
                 detail='Bad request',
                 description='Your request is wrong',
                 additional='ABOBA'
                 ):
        super().__init__(status_code=status_code, detail=detail)
        self.description = description
        self.additional = additional
