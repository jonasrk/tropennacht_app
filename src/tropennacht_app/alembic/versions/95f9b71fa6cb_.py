"""empty message

Revision ID: 95f9b71fa6cb
Revises:
Create Date: 2024-09-19 12:58:17.710872

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "95f9b71fa6cb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users_cities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("city", sa.String(length=254), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users_cities", schema="public")
    # ### end Alembic commands ###
