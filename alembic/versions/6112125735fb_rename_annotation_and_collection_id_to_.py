"""Rename Annotation and Collection id to key

Revision ID: 6112125735fb
Revises: df7141678289
Create Date: 2018-05-06 18:10:04.499480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6112125735fb'
down_revision = 'df7141678289'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('annotation', 'id', new_column_name='key')
    op.alter_column('collection', 'id', new_column_name='key')
    op.alter_column('annotation', 'collection_id',
                    new_column_name='collection_key')


def downgrade():
    op.alter_column('annotation', 'key', new_column_name='id')
    op.alter_column('collection', 'key', new_column_name='id')
    op.alter_column('annotation', 'collection_key',
                    new_column_name='collection_id')
