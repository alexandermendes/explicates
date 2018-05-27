"""Add indexes to Annotation table

Revision ID: 0585e7d309a1
Revises: 13ad0b8849e5
Create Date: 2018-05-27 19:44:10.461247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0585e7d309a1'
down_revision = '13ad0b8849e5'
branch_labels = None
depends_on = None


def upgrade():
    sql = ("""
        CREATE or REPLACE FUNCTION lang_cast(VARCHAR) RETURNS regconfig
            AS 'select cast($1 as regconfig)'
            LANGUAGE SQL
            IMMUTABLE
            RETURNS NULL ON NULL INPUT;

        CREATE INDEX idx_annotation_body
            ON annotation
            USING gin (to_tsvector(lang_cast(language), _data -> 'body'));

        CREATE INDEX idx_annotation_target
            ON annotation
            USING gin (to_tsvector(lang_cast(language), _data -> 'target'));
    """)
    op.execute(sql)

def downgrade():
    op.drop_index('idx_annotation_body')
    op.drop_index('idx_annotation_target')
