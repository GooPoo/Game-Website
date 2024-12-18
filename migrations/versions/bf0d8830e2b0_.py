"""empty message

Revision ID: bf0d8830e2b0
Revises: 7112076d18d2
Create Date: 2024-10-24 12:41:50.109505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf0d8830e2b0'
down_revision = '7112076d18d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_score', schema=None) as batch_op:
        batch_op.add_column(sa.Column('score', sa.Integer(), server_default='0'))

    with op.batch_alter_table('game_score_api', schema=None) as batch_op:
        batch_op.add_column(sa.Column('score', sa.Integer(), server_default='0'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_score_api', schema=None) as batch_op:
        batch_op.drop_column('score')

    with op.batch_alter_table('game_score', schema=None) as batch_op:
        batch_op.drop_column('score')

    # ### end Alembic commands ###
