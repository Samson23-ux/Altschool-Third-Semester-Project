from uuid import UUID
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.users import User
from app.utils import hash_password, post_to_json, read_file
from app.schemas.users import UserCreateV1, UserUpdateV1
from app.core.exceptions import (
    UserExistError,
    UserNotFoundError,
    UsersNotFoundError,
    ServerError,
)


class UserService:
    async def get_users(
        self,
        offset: int,
        limit: int,
        db: Session,
        order: str,
        sort: str | None = None,
    ) -> list[User]:
        if sort is not None:
            if order == "desc":
                sort_cte = db.query(User).order_by(desc(sort)).cte("sort_cte")
            else:
                sort_cte = db.query(User).order_by(sort).cte("sort_cte")

        users = (
            db.query(User)
            .join(sort_cte, User.id == sort_cte.c.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not users:
            raise UsersNotFoundError()
        return users

    async def search_users(
        self, q: str, offset: int, limit: int, db: Session
    ) -> list[User]:
        ts_query = func.websearch_to_tsquery("english", q)
        search_rank = func.ts_rank_cd(User.username_search, ts_query).label(
            "search_rank"
        )

        search_cte = (
            db.query(User, search_rank)
            .filter(User.username_search.op("@@")(ts_query))
            .order_by(search_rank.desc())
            .cte("search_cte")
        )

        search_result = (
            db.query(User)
            .join(search_cte, User.id == search_cte.c.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not search_result:
            raise UsersNotFoundError()
        return search_result

    async def get_user_by_username(self, username: str, db: Session) -> User:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_by_id(self, user_id: UUID, db: Session) -> User:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_likes(self, user_id: UUID, db: Session):
        user = await self.get_user_by_id(user_id, db)

        if not user:
            raise UserNotFoundError()

        user_likes = user.likes
        posts = []

        for like in user_likes:
            posts.append(like.post)

        for p in posts:
            post = post_to_json(p)
            post["images"] = []
            post["likes"] = p.likes

            if p.images:
                for img in p.images:
                    image = await read_file(img)
                    post["images"].append(image)

        return posts

    async def create_user(self, user_create: UserCreateV1, db: Session) -> User:
        user_by_email = (
            db.query(User.email).filter(User.email == user_create.email).first()
        )

        if user_by_email:
            raise UserExistError()

        user_create.password = hash_password(user_create.password)

        user_db = User(**user_create.model_dump())

        try:
            db.add(user_db)
            db.flush()
            db.refresh(user_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        user = await self.get_user_by_id(user_db.id, db)
        return user

    async def update_user(
        self, user_id: UUID, user_update: UserUpdateV1, db: Session
    ) -> User:
        user_db = await self.get_user_by_id(user_id, db)
        if not user_db:
            raise UserNotFoundError()

        if user_update.email:
            user_by_email = (
                db.query(User.email).filter(User.email == user_update.email).first()
            )
            if user_by_email:
                raise UserExistError()

        user_update_dict = user_update.model_dump(exclude_unset=True)

        for k, v in user_update_dict.items():
            setattr(user_db, k, v)

        try:
            db.add(user_db)
            db.flush()
            db.refresh(user_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        user = await self.get_user_by_id(user_id, db)
        return user

    async def delete_user(self, user_id: UUID, db: Session):
        user_db = await self.get_user_by_id(user_id, db)
        if not user_db:
            raise UserNotFoundError()

        try:
            db.delete(user_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e


user_service = UserService()
