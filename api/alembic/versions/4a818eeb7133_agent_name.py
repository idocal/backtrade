"""agent name

Revision ID: 4a818eeb7133
Revises: 9ce9ad551fef
Create Date: 2022-03-15 22:55:11.973364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4a818eeb7133"
down_revision = "9ce9ad551fef"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("agents", sa.Column("name", sa.String()))


def downgrade():
    op.drop_column("agents", "name")
