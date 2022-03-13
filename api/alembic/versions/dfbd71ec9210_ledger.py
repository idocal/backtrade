"""ledger

Revision ID: dfbd71ec9210
Revises: 9f0b4ede056a
Create Date: 2022-03-13 18:29:21.137318

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "dfbd71ec9210"
down_revision = "9f0b4ede056a"
branch_labels = None
depends_on = None

from api.db.models import Agent


def upgrade():
    op.drop_table(Agent.__tablename__)
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)


def downgrade():
    op.drop_table(Agent.__tablename__)
