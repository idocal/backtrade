"""init

Revision ID: 866fad61fb3c
Revises: 
Create Date: 2022-03-28 21:36:39.665136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '866fad61fb3c'
down_revision = None
branch_labels = None
depends_on = None

from api.db.models import Agent, Trade, Balance


def upgrade():
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)

    cols = [c for c in Balance.__table__.columns]
    op.create_table(Balance.__tablename__, *cols)

    cols = [c for c in Trade.__table__.columns]
    op.create_table(Trade.__tablename__, *cols)


def downgrade():
    op.drop_table(Agent.__tablename__)
    op.drop_table(Balance.__tablename__)
    op.drop_table(Trade.__tablename__)
