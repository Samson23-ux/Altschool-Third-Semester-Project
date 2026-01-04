from uuid import UUID
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, Query, UploadFile, File

from app.services.posts import post_service
from app.utils import get_db, post_to_json
from app.schemas.posts import PostCreateV1, PostUpdateV1, LikeCreate, Response

post_router_v1 = APIRouter()


create_post_desc = """
Upload images at /posts/images/upload/ if post has images
and send name as the image attribute value in PostCreateV1 model
"""

@post_router_v1.get("/posts/feed/", status_code=200, response_model=Response)
async def get_posts(
    sort: str = Query(
        default=None, description="sort by date created(e.g sort=created_at)"
    ),
    order: str = Query(default=None, description="order in asc or desc"),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    db: Session = Depends(get_db),
):
    posts = await post_service.get_posts(offset, limit, db, sort, order)
    return Response(message="Feed loaded successfully", data=posts)


@post_router_v1.get("/posts/search/", status_code=200, response_model=Response)
async def search_posts(
    q: str = Query(..., description="search posts with title"),
    sort: str = Query(
        default=None, description="sort by date created(e.g sort=created_at)"
    ),
    order: str = Query(default=None, description="order in asc or desc"),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    db: Session = Depends(get_db),
):
    posts = await post_service.search_posts(q, offset, limit, db, sort, order)
    return Response(message="Posts retrieved successfully", data=posts)


@post_router_v1.get("/posts/{post_id}/", status_code=200, response_model=Response)
async def get_post_by_id(post_id: UUID, db: Session = Depends(get_db)):
    post = await post_service.get_post_by_id(post_id, db)
    return Response(message="Post retrieved successfully", data=post)


@post_router_v1.get("/posts/{post_id}/images/{image_url}/load/", status_code=200, response_class=FileResponse)
async def get_post_image(post_id: UUID, image_url: str, db: Session = Depends(get_db)):
    file_path = await post_service.load_image(post_id, image_url, db)
    return FileResponse(path=file_path)


@post_router_v1.post(
    "/posts/",
    status_code=201,
    response_model=Response,
    description=create_post_desc,
)
async def create_post(post_create: PostCreateV1, db: Session = Depends(get_db)):
    post_db = await post_service.create_post(post_create, db)
    post = post_to_json(post_db)
    return Response(message="Post created successfully", data=post)


@post_router_v1.post("/posts/images/upload/", status_code=201, response_model=Response)
async def upload_images(
    post_images: list[UploadFile] = File(..., description="Upload post images")
):
    images = await post_service.upload_image(post_images)
    return Response(message="Images uploaded successfully", data=images)


@post_router_v1.post("/posts/{post_id}/like/", status_code=201, response_model=Response)
async def like_post(
    post_id: UUID, like_create: LikeCreate, db: Session = Depends(get_db)
):
    like = await post_service.like_post(post_id, like_create, db)
    return Response(message="Post liked successfully", data=like)


@post_router_v1.patch("/posts/{post_id}/", status_code=200, response_model=Response)
async def update_post(
    post_id: UUID, post_update: PostUpdateV1, db: Session = Depends(get_db)
):
    post = await post_service.update_post(post_id, post_update, db)
    return Response(message="Post updated successfully", data=post)


@post_router_v1.delete("/posts/{post_id}/unlike/{user_id}/", status_code=204)
async def delete_like(post_id: UUID, user_id: UUID, db: Session = Depends(get_db)):
    await post_service.delete_like(post_id, user_id, db)
    return Response(message="Post unliked successfully")


@post_router_v1.delete("/posts/{post_id}/images/{image_name}/", status_code=204)
async def delete_image(post_id: UUID, image_name: str, db: Session = Depends(get_db)):
    await post_service.delete_image(post_id, image_name, db)
    return Response(message="Image deleted successfully")


@post_router_v1.delete("/posts/{post_id}/", status_code=204)
async def delete_post(post_id: UUID, db: Session = Depends(get_db)):
    await post_service.delete_post(post_id, db)
    return Response(message="Post deleted successfully")
