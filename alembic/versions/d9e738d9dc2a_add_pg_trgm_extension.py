"""add pg_trgm extension

Revision ID: d9e738d9dc2a
Revises: 6e00485a625f
Create Date: 2026-01-03 21:11:14.293802

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd9e738d9dc2a'
down_revision: Union[str, Sequence[str], None] = '6e00485a625f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
