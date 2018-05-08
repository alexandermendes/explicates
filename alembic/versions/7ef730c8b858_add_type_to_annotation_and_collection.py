"""Add type to Annotation and Collection

Revision ID: 7ef730c8b858
Revises: 6112125735fb
Create Date: 2018-05-08 12:15:54.563003

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7ef730c8b858'
down_revision = '6112125735fb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('annotation', sa.Column('type', postgresql.JSONB,
                                          default='Annotation'))
    op.add_column('collection', sa.Column('type', postgresql.JSONB,
                                          default='AnnotationCollection'))


def downgrade():
    op.drop_column('annotation', 'type')
    op.drop_column('collection', 'type')
