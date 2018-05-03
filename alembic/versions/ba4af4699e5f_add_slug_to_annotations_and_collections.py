"""Add slug to annotations and collections

Revision ID: ba4af4699e5f
Revises: c2603e3297e1
Create Date: 2018-05-03 21:44:46.020241

"""
from alembic import op
import sqlalchemy as sa

def make_uuid():
    return str(uuid.uuid4())

# revision identifiers, used by Alembic.
revision = 'ba4af4699e5f'
down_revision = 'c2603e3297e1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('annotation', sa.Column('slug', sa.Unicode, unique=True,
                                          default=make_uuid))
    op.add_column('collection', sa.Column('slug', sa.Unicode, unique=True,
                                          default=make_uuid))


def downgrade():
    op.drop_column('annotation', 'slug')
    op.drop_column('collection', 'slug')
