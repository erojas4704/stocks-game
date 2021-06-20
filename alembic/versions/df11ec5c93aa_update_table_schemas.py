"""update table schemas

Revision ID: df11ec5c93aa
Revises: 
Create Date: 2021-06-19 17:23:01.118327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df11ec5c93aa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('games', sa.Column('winner_id',
        sa.Integer,
        sa.ForeignKey('users.id', ondelete="cascade")
    ))

    op.add_column('players', sa.Column('final_value',
        sa.Float,
        default = 0
    ))

    op.add_column('players', sa.Column('final_standing',
        sa.Integer
    ))

    op.add_column('users', sa.Column('wins', sa.Integer, default=0))
    op.add_column('users', sa.Column('played', sa.Integer, default=0))
    op.add_column('users', sa.Column('total_return', sa.Float, default=0))
    op.add_column('users', sa.Column('trades', sa.Integer, default=0))
    op.add_column('users', sa.Column('buys', sa.Integer, default=0))
    op.add_column('users', sa.Column('sells', sa.Integer, default=0))

    pass


def downgrade():
    op.drop_column('games', 'winner_id')
    op.drop_column('players', 'final_value')
    op.drop_column('players', 'final_standing')
    op.drop_column('users', 'wins')
    op.drop_column('users', 'played')
    op.drop_column('users', 'total_return')
    op.drop_column('users', 'trades')
    op.drop_column('users', 'buys')
    op.drop_column('users', 'sells')

    pass
