from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

from app.services.users import user_service
from app.core.exceptions import ServerError
from app.utils import get_db, users_to_json, user_to_json
from app.schemas.users import UserCreateV1, UserUpdateV1, Response

user_router_v1 = APIRouter()


@user_router_v1.get("/users/", status_code=200, response_class=Response)
async def get_users(
    sort: str = Query(default=None, description="sort by username"),
    order: str = Query(default=None, description="order in asc or desc"),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    db: Session = Depends(get_db),
):
    users = await user_service.get_users(offset, limit, db, order, sort)
    users_out = users_to_json(users)
    return Response(message="Users retrieved successfully", data=users_out)


@user_router_v1.get("/users/", status_code=200, response_class=Response)
async def get_users_by_username(
    q: str = Query(..., description="search for users by username"),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    db: Session = Depends(get_db),
):
    search = await user_service.get_users_by_username(q, offset, limit, db)
    users = users_to_json(search)
    return Response(message="Users retrieved successfully", data=users)


@user_router_v1.get("/users/{username}/", status_code=200, response_class=Response)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user_db = await user_service.get_user_by_username(username, db)
    user = user_to_json(user_db)
    return Response(message="User retrieved successfully", data=user)


@user_router_v1.get("/users/{user_id}/", status_code=200, response_class=Response)
async def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    user_db = await user_service.get_user_by_id(user_id, db)
    user = user_to_json(user_db)
    return Response(message="User retrieved successfully", data=user)


@user_router_v1.get("/users/{user_id}/likes/", status_code=200, response_class=Response)
async def get_user_likes(user_id: UUID, db: Session = Depends(get_db)):
    posts = await user_service.get_user_likes(user_id, db)
    return Response(message="Liked posts retrieved successfully", data=posts)


@user_router_v1.post("/users/", status_code=201, response_class=Response)
async def create_user(user_create: UserCreateV1, db: Session = Depends(get_db)):
    try:
        user_db = await user_service.create_user(user_create, db)
        db.commit()
        user = user_to_json(user_db)
        return Response(message="User created successfully", data=user)
    except Exception as e:
        db.rollback()
        raise ServerError() from e


@user_router_v1.patch("/users/{user_id}/", status_code=200, response_class=Response)
async def update_user(
    user_id: UUID, user_update: UserUpdateV1, db: Session = Depends(get_db)
):
    try:
        user_db = await user_service.update_user(user_id, user_update, db)
        db.commit()
        user = user_to_json(user_db)
        return Response(message="User updated successfully", data=user)
    except Exception as e:
        db.rollback()
        raise ServerError() from e


@user_router_v1.delete("/users/{user_id}/", status_code=204)
async def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    try:
        user_service.delete_user(user_id, db)
        db.commit()
        return Response(message="User deleted successfully")
    except Exception as e:
        db.rollback()
        raise ServerError() from e
