"""add menus.timestamp

Revision ID: ef8d314c1576
Revises: 4b0aa5204563
Create Date: 2023-09-21 22:12:58.832154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef8d314c1576'
down_revision = '4b0aa5204563'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menus', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menus', schema=None) as batch_op:
        batch_op.drop_column('timestamp')

    # ### end Alembic commands ###
