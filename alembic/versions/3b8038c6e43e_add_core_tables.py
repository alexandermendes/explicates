"""Add core tables

Revision ID: 3b8038c6e43e
Revises:
Create Date: 2018-05-13 02:05:16.003066

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '3b8038c6e43e'
down_revision = None
branch_labels = None
depends_on = None
from sqlalchemy.dialects import postgresql


def make_timestamp():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def make_uuid():
    return str(uuid.uuid4())


def upgrade():
    op.create_table(
        'collection',
        sa.Column('key', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=False, unique=True,
                  default=make_uuid),
        sa.Column('created', sa.Text(), default=make_timestamp),
        sa.Column('modified', sa.Text(), nullable=True),
        sa.Column('_data', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('deleted', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('key')
    )

    op.create_table(
        'annotation',
        sa.Column('key', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=False, unique=True,
                  default=make_uuid),
        sa.Column('created', sa.Text(), default=make_timestamp),
        sa.Column('modified', sa.Text(), nullable=True),
        sa.Column('_data', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('deleted', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('key'),
        sa.Column('collection_key', sa.Integer(),
                  sa.ForeignKey('collection.key'), nullable=False)
    )


def downgrade():
    op.drop_table('annotation')
    op.drop_table('collection')
