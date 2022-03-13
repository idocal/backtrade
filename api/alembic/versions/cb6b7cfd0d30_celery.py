"""celery

Revision ID: cb6b7cfd0d30
Revises: b1d398ab97d5
Create Date: 2022-03-13 14:28:33.387541

"""
from alembic import op
import sqlalchemy as sa
from api.db.models import Agent

# revision identifiers, used by Alembic.
revision = 'cb6b7cfd0d30'
down_revision = 'b1d398ab97d5'
branch_labels = None
depends_on = None


def upgrade():
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)


def downgrade():
    op.drop_table(Agent.__tablename__)
