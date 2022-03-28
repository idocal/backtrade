"""ledger table

Revision ID: d592ffe8f7b8
Revises: 4a818eeb7133
Create Date: 2022-03-24 08:59:11.015435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from db.models import Agent, Balance, Trade

revision = "d592ffe8f7b8"
down_revision = "4a818eeb7133"
branch_labels = None
depends_on = None


def upgrade():

    op.drop_table(Agent.__tablename__)
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)

    # op.drop_table(Ledger.__tablename__)
    cols = [c for c in Balance.__table__.columns]
    op.create_table(Balance.__tablename__, *cols)

    cols = [c for c in Trade.__table__.columns]
    op.create_table(Trade.__tablename__, *cols)


def downgrade():
    pass
