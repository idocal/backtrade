"""symbolstype

Revision ID: 9ce9ad551fef
Revises: dfbd71ec9210
Create Date: 2022-03-13 20:23:15.539688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = '9ce9ad551fef'
down_revision = 'dfbd71ec9210'
branch_labels = None
depends_on = None

from api.db.models import Agent


def upgrade():
    op.drop_table(Agent.__tablename__)
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)


def downgrade():
    op.drop_table(Agent.__tablename__)
