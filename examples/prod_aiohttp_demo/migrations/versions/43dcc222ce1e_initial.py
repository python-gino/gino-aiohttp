"""initial

Revision ID: 43dcc222ce1e
Revises:
Create Date: 2020-04-17 19:07:30.835946

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "43dcc222ce1e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "prod_aiohttp_demo_users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("nickname", sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("prod_aiohttp_demo_users")
