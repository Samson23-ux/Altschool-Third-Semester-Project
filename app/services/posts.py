from uuid import UUID, uuid4
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

from app.models.users import User
from app.services.users import user_service
from app.models.posts import Post, Image, Like
from app.schemas.posts import PostCreateV1, PostUpdateV1, PostInDBV1, LikeCreate
from app.utils import post_to_json, generate_file_path, write_file, delete_file, like_to_json
from app.core.exceptions import (
    PostNotFoundError,
    PostsNotFoundError,
    UserNotSignedUpError,
    UserNotFoundError,
    ServerError,
    InvalidImageUrlError
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
        is_sort = False
        if sort:
            if order == "desc":
                sort_cte = db.query(Post).order_by(desc(sort)).cte("sort_cte")
            else:
                sort_cte = db.query(Post).order_by(sort).cte("sort_cte")
            is_sort = True

        if is_sort:
            feed_posts_db = (
                db.query(Post)
                .join(sort_cte, Post.id == sort_cte.c.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
        else:
            feed_posts_db = db.query(Post).offset(offset).limit(limit).all()

        if not feed_posts_db:
            raise PostsNotFoundError()

        feed_posts = []
        for p in feed_posts_db:
            post = post_to_json(p)
            post["images"] = []
            post["likes"] = len(p.likes)

            if p.images:
                for img in p.images:
                    post["images"].append(img.image_url)
            feed_posts.append(post)

        return feed_posts

    async def search_posts(
        self,
        q: str,
        offset: int,
        limit: int,
        db: Session,
        sort: str | None = None,
        order: str | None = None,
    ) -> list[Post]:
        query_search = func.websearch_to_tsquery("english", q)
        rank_search = func.ts_rank(Post.content_search, query_search).label(
            "rank_search"
        )

        search_cte = (
            db.query(Post, rank_search)
            .filter(Post.content_search.op("@@")(query_search))
            .order_by(rank_search.desc())
            .cte("search_cte")
        )

        is_sort = False
        if sort:
            if order == "desc":
                sort_cte = db.query(search_cte).order_by(desc(sort)).cte("sort_cte")
            else:
                sort_cte = db.query(Post).order_by(sort).cte("sort_cte")
            is_sort = True

        if is_sort:
            search_posts = (
                db.query(Post)
                .join(sort_cte, Post.id == sort_cte.c.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
        else:
            search_posts = (
                db.query(Post)
                .join(search_cte, Post.id == search_cte.c.id)
                .offset(offset)
                .limit(limit)
                .all()
            )

        if not search_posts:
            raise PostsNotFoundError()

        posts = []
        for p in search_posts:
            post = post_to_json(p)
            post["images"] = []
            post["likes"] = len(p.likes)

            if p.images:
                for img in p.images:
                    post["images"].append(img.image_url)
            posts.append(post)

        return posts

    async def get_post_by_id(self, post_id: UUID, db: Session) -> Post:
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not post_db:
            raise PostNotFoundError()

        post = post_to_json(post_db)
        post["images"] = []
        post["likes"] = len(post_db.likes)

        if post_db.images:
            for img in post_db.images:
                post["images"].append(img.image_url)

        return post

    async def get_like(self, post_id: UUID, user_id: UUID, db: Session):
        like = (
            db.query(Like)
            .filter(and_(Like.post_id == post_id, Like.user_id == user_id))
            .first()
        )

        return like

    async def create_post(self, post_create: PostCreateV1, db: Session) -> Post:
        user = db.query(User.id).filter(User.username == post_create.username).scalar()

        if not user:
            raise UserNotSignedUpError()

        post_db = PostInDBV1(**post_create.model_dump(), created_at=datetime.now())

        post = Post(
            user_id=user,
            title=post_db.title,
            content=post_db.content,
            created_at=post_db.created_at,
        )

        if post_create.image:
            for img in post_create.image:
                image = Image(id=uuid4(), image_url=img)
                if image not in post.images:
                    post.images.append(image)

        try:
            db.add(post)
            db.flush()
            db.refresh(post)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        user_post = await self.get_post_by_id(post.id, db)
        return user_post

    async def load_image(self, post_id: UUID, image_url: str, db: Session):
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not post_db:
            raise PostNotFoundError()

        image_urls = [img.image_url for img in post_db.images]

        if image_url not in image_urls:
            raise InvalidImageUrlError()

        path = generate_file_path(image_url)
        return path

    async def like_post(
        self, post_id: UUID, like_create: LikeCreate, db: Session
    ) -> Post:
        like_db = await self.get_like(post_id, like_create.user_id, db)
        if like_db:
            return like_to_json(like_db)

        user_db = await user_service.get_user_by_id(like_create.user_id, db)
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not user_db:
            raise UserNotFoundError()

        if not post_db:
            raise PostsNotFoundError()

        like_db = Like(post_id=post_id, user_id=like_create.user_id)

        try:
            db.add(like_db)
            db.flush()
            db.refresh(like_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        like_db = await self.get_like(post_db.id, user_db.id, db)
        like = like_to_json(like_db)
        return like

    async def upload_image(self, images: UploadFile):
        images = await write_file(images)
        return images

    async def update_post(
        self, post_id: UUID, post_update: PostUpdateV1, db: Session
    ) -> Post:
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not post_db:
            raise PostsNotFoundError()

        post_update_dict = post_update.model_dump(exclude_unset=True)

        for k, v in post_update_dict.items():
            setattr(post_db, k, v)

        try:
            db.add(post_db)
            db.flush()
            db.refresh(post_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        post_db = db.query(Post).filter(Post.id == post_id).first()

        post = post_to_json(post_db)
        post["images"] = []
        post["likes"] = len(post_db.likes)

        if post_db.images:
            for img in post_db.images:
                post["images"].append(img.image_url)

        return post

    async def delete_like(self, post_id: UUID, user_id: UUID, db: Session):
        user_db = await user_service.get_user_by_id(user_id, db)
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not user_db:
            raise UserNotFoundError()

        if not post_db:
            raise PostsNotFoundError()

        like = await self.get_like(post_db.id, user_db.id, db)

        try:
            post_db.likes.remove(like)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

    async def delete_image(self, post_id: UUID, image_name: str, db: Session):
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not post_db:
            raise PostsNotFoundError()

        for img in post_db.images:
            if img.image_url == image_name:
                delete_file(image_name)

        image = db.query(Image).filter(Image.image_url == image_name).first()

        try:
            post_db.images.remove(image)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            raise ServerError() from e

    async def delete_post(self, post_id: UUID, db: Session):
        post_db = db.query(Post).filter(Post.id == post_id).first()

        if not post_db:
            raise PostsNotFoundError()

        try:
            db.delete(post_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e


post_service = PostService()
