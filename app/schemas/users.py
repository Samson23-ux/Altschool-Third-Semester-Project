from typing import Optional, Any
from pydantic import BaseModel, EmailStr

class UserBaseV1(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreateV1(UserBaseV1):
    pass

class UserInDBV1(UserBaseV1):
    pass

class PasswordUpdateV1(BaseModel):
    old_password: str
    new_password: str

class UserUpdateV1(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class Response(BaseModel):
    message: str
    data: Optional[Any] = None
