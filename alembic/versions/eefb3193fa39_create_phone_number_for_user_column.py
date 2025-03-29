"""Create phone number for user column

Revision ID: eefb3193fa39
Revises: 
Create Date: 2025-02-08 14:57:23.613716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eefb3193fa39'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(), unique=True))


def downgrade() -> None:
    op.drop_column("users", "phone_number")
