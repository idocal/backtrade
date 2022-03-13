"""celery2

Revision ID: 9f0b4ede056a
Revises: cb6b7cfd0d30
Create Date: 2022-03-13 14:40:09.085262

"""
from alembic import op
import sqlalchemy as sa
from api.db.models import Agent

# revision identifiers, used by Alembic.
revision = '9f0b4ede056a'
down_revision = 'cb6b7cfd0d30'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table(Agent.__tablename__)
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)


def downgrade():
    op.drop_table(Agent.__tablename__)

