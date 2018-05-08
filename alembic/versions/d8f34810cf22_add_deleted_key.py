"""Add deleted key

Revision ID: d8f34810cf22
Revises: 071ac95adb2f
Create Date: 2018-05-08 20:20:28.616568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8f34810cf22'
down_revision = '071ac95adb2f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('annotation', sa.Column('deleted', sa.Boolean(),
                  default=False))
    op.add_column('collection', sa.Column('deleted', sa.Boolean(),
                  default=False))
    sql = 'UPDATE annotation SET deleted=False'
    op.execute(sql)
    sql = 'UPDATE collection SET deleted=False'
    op.execute(sql)


def downgrade():
    op.drop_column('annotation', 'deleted')
    op.drop_column('collection', 'deleted')
