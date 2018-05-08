"""Fix data column

Revision ID: 5fd73c500614
Revises: d8f34810cf22
Create Date: 2018-05-08 23:02:42.489494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fd73c500614'
down_revision = 'd8f34810cf22'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('annotation', 'data', new_column_name='_data')
    op.alter_column('collection', 'data', new_column_name='_data')


def downgrade():
    op.alter_column('annotation', '_data', new_column_name='data')
    op.alter_column('collection', '_data', new_column_name='data')
