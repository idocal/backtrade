"""init

Revision ID: b1d398ab97d5
Revises: 
Create Date: 2022-03-02 00:47:14.330136

"""
from alembic import op
import sqlalchemy as sa
from api.db.models import Agent, Trade, Balance

# revision identifiers, used by Alembic.
revision = "b1d398ab97d5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)

    # op.drop_table(Ledger.__tablename__)
    cols = [c for c in Balance.__table__.columns]
    op.create_table(Balance.__tablename__, *cols)

    cols = [c for c in Trade.__table__.columns]
    op.create_table(Trade.__tablename__, *cols)


def downgrade():
    # op.drop_table(Agent.__tablename__)
    pass
