import uuid
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import (
    Column,
    VARCHAR,
    Text,
    ForeignKey,
    Table,
    UUID,
    DateTime,
    Computed,
    Index,
)

from app.database.base import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID, default=uuid.uuid4(), primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(VARCHAR(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    content_search = Column(
        TSVECTOR, Computed("to_tsvector('english', \"content\")", persisted=True)
    )
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="posts")

    likes = relationship(
        "Like",
        back_populates="post",
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )

    images = relationship(
        "Image",
        secondary="post_images",
        back_populates="posts",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    __table_args__ = (
        Index("idx_content_search", content_search, postgresql_using="gin"),
    )


class Image(Base):
    __tablename__ = "images"

    id = Column(UUID, default=uuid.uuid4(), primary_key=True)
    image_url = Column(Text, nullable=False, index=True)

    posts = relationship(
        "Post",
        secondary="post_images",
        back_populates="images",
    )


class Like(Base):
    __tablename__ = "likes"

    post_id = Column(UUID, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    liked_at = Column(DateTime, default=datetime.now(), nullable=False)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


post_image = Table(
    "post_images",
    Base.metadata,
    Column(
        "post_id", UUID, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "image_id", UUID, ForeignKey("images.id", ondelete="CASCADE"), primary_key=True
    ),
)
