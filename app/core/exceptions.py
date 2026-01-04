from fastapi import Request
from typing import Any, Callable
from fastapi.responses import JSONResponse

class AppException(Exception):
    '''Base Exception for all Errors'''
    pass

class ServerError(AppException):
    '''Internal Server Error'''
    pass

class PasswordError(AppException):
    '''User provided an invalid password'''
    pass

class UserExistError(AppException):
    '''User provided an exsisting email'''
    pass

class UsersNotFoundError(AppException):
    '''No Users found currently'''
    pass

class UserNotFoundError(AppException):
    '''User not found with the provided id'''
    pass

class UserNotSignedUpError(AppException):
    '''User not signed up'''
    pass

class PostsNotFoundError(AppException):
    '''No posts found currently'''
    pass

class PostNotFoundError(AppException):
    '''No Post found with the provided id'''
    pass

class InvalidImageUrlError(AppException):
    '''No Image found with the provided url'''
    pass

def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=status_code, content=initial_detail)

    return exception_handler
