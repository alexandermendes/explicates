"""Use single JSONB column for all modifiable content

Revision ID: 071ac95adb2f
Revises: 7ef730c8b858
Create Date: 2018-05-08 12:44:02.659987

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '071ac95adb2f'
down_revision = '7ef730c8b858'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('annotation', 'stylesheet')
    op.drop_column('annotation', 'creator')
    op.drop_column('annotation', 'target')
    op.drop_column('annotation', 'body')
    op.add_column('annotation',
                  sa.Column('data', postgresql.JSONB(astext_type=sa.Text())))

    op.drop_column('collection', 'creator')
    op.drop_column('collection', 'label')
    op.add_column('collection',
                  sa.Column('data', postgresql.JSONB(astext_type=sa.Text())))

    # Still in very early development stages so just drop current annotations
    sql = 'DELETE FROM annotation'
    op.execute(sql)
    sql = 'DELETE FROM collection'
    op.execute(sql)


def downgrade():
    op.add_column('annotation',
                  sa.Column('stylesheet',
                            postgresql.JSONB(astext_type=sa.Text()),
                            nullable=True))
    op.add_column('annotation',
                  sa.Column('creator', postgresql.JSONB(astext_type=sa.Text()),
                            nullable=True))
    op.add_column('annotation',
                  sa.Column('target', postgresql.JSONB(astext_type=sa.Text()),
                            nullable=False))
    op.add_column('annotation',
                  sa.Column('body', postgresql.JSONB(astext_type=sa.Text()),
                            nullable=False))
    op.drop_column('annotation', 'data')

    op.add_column('collection',
                  sa.Column('label', sa.Text(), nullable=True))
    op.add_column('collection',
                  sa.Column('creator', postgresql.JSONB(astext_type=sa.Text()),
                            nullable=True))

    op.drop_column('collection', 'data')
