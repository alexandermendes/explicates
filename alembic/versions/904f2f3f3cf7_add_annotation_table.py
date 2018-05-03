"""Add annotation table

Revision ID: 904f2f3f3cf7
Revises:
Create Date: 2018-05-03 18:53:21.230106

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '904f2f3f3cf7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('annotation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('body', postgresql.JSONB(astext_type=sa.Text()),
                                           nullable=False),
        sa.Column('target', postgresql.JSONB(astext_type=sa.Text()),
                                             nullable=False),
        sa.Column('created', sa.Text(), nullable=True),
        sa.Column('creator', postgresql.JSONB(astext_type=sa.Text()),
                                              nullable=True),
        sa.Column('modified', sa.Text(), nullable=True),
        sa.Column('stylesheet', postgresql.JSONB(astext_type=sa.Text()),
                                                 nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('annotation')