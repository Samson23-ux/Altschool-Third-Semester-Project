import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Column, VARCHAR, Text, Computed, Index, UUID

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, default=uuid.uuid4(), primary_key=True)
    username = Column(VARCHAR(50), nullable=False)
    email = Column(VARCHAR(50), unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)

    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )
    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "idx_username_trgm",
            username,
            postgresql_using="gin",
            postgresql_ops={"username": "gin_trgm_ops"},
        ),
    )
