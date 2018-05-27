"""Add language to Annotation

Revision ID: 13ad0b8849e5
Revises: 3b8038c6e43e
Create Date: 2018-05-27 17:20:14.775557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13ad0b8849e5'
down_revision = '3b8038c6e43e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('annotation', sa.Column('language', sa.Text))
    sql = "update annotation set language='english'"
    op.execute(sql)

def downgrade():
    op.drop_column('annotation', 'language')
