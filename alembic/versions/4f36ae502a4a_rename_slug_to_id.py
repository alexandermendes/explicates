"""Rename slug to id

Revision ID: 4f36ae502a4a
Revises: 5fd73c500614
Create Date: 2018-05-12 04:05:51.166561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f36ae502a4a'
down_revision = '5fd73c500614'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('annotation', 'slug', new_column_name='id')
    op.alter_column('collection', 'slug', new_column_name='id')


def downgrade():
    op.alter_column('annotation', 'id', new_column_name='slug')
    op.alter_column('collection', 'id', new_column_name='slug')
