from uuid import UUID
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

from app.models.users import User
from app.services.users import user_service
from app.models.posts import Post, Image, Like
from app.schemas.posts import PostCreateV1, PostUpdateV1, PostInDBV1, LikeCreate
from app.utils import post_to_json, read_file, write_file, delete_file
from app.core.exceptions import (
    PostNotFoundError,
    PostsNotFoundError,
    UserNotSignedUpError,
    UserNotFoundError,
)


class PostService:
    async def get_posts(
        self,
        offset: int,
        limit: int,
        db: Session,
        sort: str | None = None,
        order: str | None = None,
    ) -> list[Post]:
        if sort:
            if order == "desc":
                sort_cte = db.query(Post).order_by(desc(sort)).cte("sort_cte")
            else:
                sort_cte = db.query(Post).order_by(sort).cte("sort_cte")

        feed_posts = (
            db.query(Post)
            .join(sort_cte, Post.id == sort_cte.c.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not feed_posts:
            raise PostsNotFoundError()

        for p in feed_posts:
            post = post_to_json(p)
            post["images"] = []

            if p.images:
                for img in p.images:
                    image = await read_file(img)
                    post["images"].append(image)

        return feed_posts

    async def get_search_posts(
        self,
        q: str,
        offset: int,
        limit: int,
        db: Session,
        sort: str | None = None,
        order: str | None = None,
    ) -> list[Post]:
        query_search = func.to_tsquery("english", q)
        rank_search = func.ts_rank_cd(Post.title_search, query_search).label(
            "rank_search"
        )

        search_cte = (
            db.query(Post, rank_search)
            .filter(Post.title_search.op("@@")(query_search))
            .order_by(rank_search.desc())
            .cte("search_cte")
        )

        if sort:
            if order == "desc":
                sort_cte = db.query(search_cte).order_by(desc(sort)).cte("sort_cte")
            else:
                sort_cte = db.query(Post).order_by(sort).cte("sort_cte")

        search_posts = (
            db.query(Post)
            .join(sort_cte, Post.id == sort_cte.c.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not search_posts:
            raise PostsNotFoundError()

        for p in search_posts:
            post = post_to_json(p)
            post["images"] = []

            if p.images:
                for img in p.images:
                    image = await read_file(img)
                    post["images"].append(image)

        return search_posts

    async def get_post_by_id(self, post_id: UUID, db: Session) -> Post:
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not post_db:
            raise PostNotFoundError()

        post = post_to_json(post_db)
        post["images"] = []

        if post_db.images:
            for img in post_db.images:
                image = await read_file(img)
                post["images"].append(image)

        return post

    async def get_like(self, post_id: UUID, user_id: UUID, db: Session):
        like = (
            db.query(Like)
            .filter(and_(Like.post_id == post_id, Like.user_id == user_id))
            .first()
        )

        return like

    async def create_post(self, post_create: PostCreateV1, db: Session) -> Post:
        user = (
            db.query(User.username)
            .filter(User.username == post_create.username)
            .first()
        )

        if not user:
            raise UserNotSignedUpError()

        post_db = PostInDBV1(created_at=datetime.now())

        post = Post(**post_db.model_dump())

        if post_create.image:
            for img in post_create.image:
                image = Image(image_url=img)
                post.images = image

        db.add(post)
        db.flush()
        db.refresh(post)

        user_post = await self.get_post_by_id(post.id, db)
        return user_post

    async def like_post(
        self, post_id: UUID, like_create: LikeCreate, db: Session
    ) -> Post:
        like_db = await self.get_like(post_id, like_create.user_id, db)
        if like_db:
            return like_db

        user_db = await user_service.get_user_by_id(like_create.user_id, db)
        post_db = await self.get_post_by_id(post_id, db)

        if not user_db:
            raise UserNotFoundError()

        if not post_db:
            raise PostsNotFoundError()

        like_db = Like(post_id=post_id, user_id=like_create.user_id)
        db.add(like_db)
        db.flush()
        db.refresh(like_db)

        like = await self.get_like(post_db.id, user_db.id, db)
        return like

    async def upload_image(self, images: UploadFile):
        images = await write_file(images)
        return images

    async def update_post(
        self, post_id: UUID, post_update: PostUpdateV1, db: Session
    ) -> Post:
        post_db = await self.get_post_by_id(post_id, db)

        if not post_db:
            raise PostsNotFoundError()

        post_update_dict = post_update.model_dump(exclude_unset=True)

        for k, v in post_update_dict.items():
            setattr(post_db, k, v)

        db.add(post_db)
        db.flush()
        db.refresh(post_db)

        post_update_db = await self.get_post_by_id(post_id, db)

        post = post_to_json(post_update_db)
        post["images"] = []

        if post_update_db.images:
            for img in post_update_db.images:
                image = await read_file(img)
                post["images"].append(image)

        return post

    async def delete_like(self, post_id: UUID, user_id: UUID, db: Session):
        user_db = await user_service.get_user_by_id(user_id, db)
        post_db = await self.get_post_by_id(post_id, db)

        if not user_db:
            raise UserNotFoundError()

        if not post_db:
            raise PostsNotFoundError()

        like = await self.get_like(post_db.id, user_db.id, db)

        post_db.likes.remove(like)

    async def delete_image(self, post_id: UUID, image_name: str, db: Session):
        post_db = await self.get_post_by_id(post_id, db)

        if not post_db:
            raise PostsNotFoundError()

        for img in post_db.images:
            if img == image_name:
                delete_file(image_name)

        image = db.query(Image).filter(Image.image_url == image_name).first()
        post_db.images.remove(image)

    async def delete_post(self, post_id: UUID, db: Session):
        post_db = await self.get_post_by_id(post_id, db)

        if not post_db:
            raise PostsNotFoundError()

        db.delete(post_db)


post_service = PostService()
