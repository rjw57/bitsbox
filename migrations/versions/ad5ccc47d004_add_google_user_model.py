"""add Google user model

Revision ID: ad5ccc47d004
Revises: fe028940e19b
Create Date: 2017-02-01 08:38:14.233344

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils.types.url


# revision identifiers, used by Alembic.
revision = 'ad5ccc47d004'
down_revision = 'fe028940e19b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('google_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unique_id', sa.Unicode(), nullable=False),
    sa.Column('email', sa.Unicode(), nullable=False),
    sa.Column('email_verified', sa.Boolean(), nullable=False),
    sa.Column('name', sa.Unicode(), nullable=False),
    sa.Column('picture_url', sqlalchemy_utils.types.url.URLType(), nullable=False),
    sa.Column('given_name', sa.Unicode(), nullable=False),
    sa.Column('family_name', sa.Unicode(), nullable=False),
    sa.Column('locale', sa.Unicode(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('unique_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('google_users')
    # ### end Alembic commands ###
