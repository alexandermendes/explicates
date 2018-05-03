"""Add collection table

Revision ID: c2603e3297e1
Revises: 904f2f3f3cf7
Create Date: 2018-05-03 21:04:55.111080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2603e3297e1'
down_revision = '904f2f3f3cf7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('collection',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.Text(), nullable=True),
        sa.Column('label', sa.Text(), nullable=True),
        sa.Column('creator', postgresql.JSONB(astext_type=sa.Text()),
                                              nullable=True),
        sa.Column('modified', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('collection')
