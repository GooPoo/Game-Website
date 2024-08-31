"""Addition of Game, Guess, Gamewordofday Tables

Revision ID: cd8da68a7776
Revises: e7d0be82888c
Create Date: 2024-07-12 19:07:57.818603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd8da68a7776'
down_revision = 'e7d0be82888c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gamewordofday',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(length=5), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('game_word_id', sa.Integer(), nullable=False),
    sa.Column('complete', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['game_word_id'], ['gamewordofday.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('guess',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('guess_number', sa.Integer(), nullable=False),
    sa.Column('guess_word', sa.String(length=5), nullable=False),
    sa.Column('guess_score', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('guess', schema=None) as batch_op:
        batch_op.create_index('idx_game_id', ['game_id'], unique=False)
        batch_op.create_index('idx_game_id_guess_number', ['game_id', 'guess_number'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('guess', schema=None) as batch_op:
        batch_op.drop_index('idx_game_id_guess_number')
        batch_op.drop_index('idx_game_id')

    op.drop_table('guess')
    op.drop_table('game')
    op.drop_table('gamewordofday')
    # ### end Alembic commands ###
