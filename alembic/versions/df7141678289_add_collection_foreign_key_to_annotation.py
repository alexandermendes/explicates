"""Add collection foreign key to annotation

Revision ID: df7141678289
Revises: ba4af4699e5f
Create Date: 2018-05-03 22:23:15.603690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df7141678289'
down_revision = 'ba4af4699e5f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('annotation', sa.Column('collection_id', sa.Integer,
                  sa.ForeignKey('collection.id')))

    # Still in very early development stages so just drop current annotations
    sql = 'DELETE FROM annotation'
    op.execute(sql)


def downgrade():
    op.drop_column('annotation', 'collection_id')
