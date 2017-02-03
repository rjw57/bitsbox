"""add uniqueness constraints

Revision ID: e59c406395d2
Revises: ad5ccc47d004
Create Date: 2017-02-02 16:00:24.237353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e59c406395d2'
down_revision = 'ad5ccc47d004'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('layout_items', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_layout_items_layout_spec_item_path', ['layout_id', 'spec_item_path'])

    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_locations_cabinet_layout_item', ['cabinet_id', 'layout_item_id'])

    with op.batch_alter_table('resource_links', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_resource_links_name_collection', ['name', 'collection_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resource_links', schema=None) as batch_op:
        batch_op.drop_constraint('uq_resource_links_name_collection', type_='unique')

    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.drop_constraint('uq_locations_cabinet_layout_item', type_='unique')

    with op.batch_alter_table('layout_items', schema=None) as batch_op:
        batch_op.drop_constraint('uq_layout_items_layout_spec_item_path', type_='unique')

    # ### end Alembic commands ###