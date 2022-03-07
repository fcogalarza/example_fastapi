"""create post table

Revision ID: b778170abd71
Revises: 
Create Date: 2022-03-06 22:55:22.228913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b778170abd71"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
    )

    pass


def downgrade():
    op.drop_table("posts")
    pass
