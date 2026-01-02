from pathlib import Path
from fastapi import UploadFile
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder

from app.models.users import User
from app.models.posts import Post
from app.database.session import SessionLocal

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def users_to_json(users: list[User]):
    return [jsonable_encoder(u, exclude={'password'}) for u in users]

def user_to_json(user: User):
    return jsonable_encoder(user, exclude={'password'})

def post_to_json(post: Post):
    return jsonable_encoder(post)

def write_file(image_file: list[UploadFile]):
    image_urls = []
    with open("app\\uploads\\images\\", "wb+") as img:
        for image in image_file:
            img.write(image.file.read())
            image_urls.append(image.filename)
    return image_urls

def read_file(filename: str):
    with open(f"app\\uploads\\images\\{filename}", "r") as img:
        image = img.read()
    return image

def delete_file(filename: str):
    file = Path(f"app\\uploads\\images\\{filename}")
    if file.exists():
        file.unlink()
