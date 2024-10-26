"""empty message

Revision ID: da9de256d503
Revises: fd134ae7ee1c
Create Date: 2024-10-23 13:13:38.088659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da9de256d503'
down_revision = 'fd134ae7ee1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('api_token', sa.String(length=64), nullable=True))
        batch_op.create_index('idx_api_token', ['api_token'], unique=False)
        batch_op.create_unique_constraint('uq_user_api_token', ['api_token'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_index('idx_api_token')
        batch_op.drop_column('api_token')

    # ### end Alembic commands ###