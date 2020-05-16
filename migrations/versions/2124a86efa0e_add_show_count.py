"""add_show_count

Revision ID: 2124a86efa0e
Revises: 5163db6a838b
Create Date: 2020-05-09 17:01:47.940460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2124a86efa0e'
down_revision = '5163db6a838b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('show', 'start_time')
    op.add_column('venue', sa.Column('num_shows', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'num_shows')
    op.add_column('show', sa.Column('start_time', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###