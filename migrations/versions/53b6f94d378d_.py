"""empty message

Revision ID: 53b6f94d378d
Revises: 3f5266cda5a3
Create Date: 2015-01-12 09:20:50.308664

"""

# revision identifiers, used by Alembic.
revision = '53b6f94d378d'
down_revision = '3f5266cda5a3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'action_trigger', 'trigger', ['trigger_id'], ['triggerid'])
    op.create_foreign_key(None, 'action_trigger', 'action', ['action_id'], ['actionid'])
    op.create_foreign_key(None, 'area_itemtype', 'itemtype', ['itemtype_id'], ['itemtypeid'])
    op.create_foreign_key(None, 'area_itemtype', 'area', ['area_id'], ['areaid'])
    op.create_foreign_key(None, 'area_service', 'area', ['area_id'], ['areaid'])
    op.create_foreign_key(None, 'area_service', 'service', ['service_id'], ['serviceid'])
    op.create_foreign_key(None, 'aws', 'area', ['area_id'], ['areaid'])
    op.create_foreign_key(None, 'email_receiver', 'emailschedule', ['email_id'], ['emailscheduleid'])
    op.create_foreign_key(None, 'email_receiver', 'receiver', ['receiver_id'], ['receiverid'])
    op.create_foreign_key(None, 'email_report', 'report', ['report_id'], ['reportid'])
    op.create_foreign_key(None, 'email_report', 'emailschedule', ['email_id'], ['emailscheduleid'])
    op.create_foreign_key(None, 'emailschedule', 'user', ['user_id'], ['userid'])
    op.create_foreign_key(None, 'host', 'area', ['area_id'], ['areaid'])
    op.create_foreign_key(None, 'host', 'service', ['service_id'], ['serviceid'])
    op.create_foreign_key(None, 'host_itemtype', 'itemtype', ['itemtype_id'], ['itemtypeid'])
    op.create_foreign_key(None, 'host_itemtype', 'host', ['host_id'], ['hostid'])
    op.create_foreign_key(None, 'item', 'host', ['host_id'], ['hostid'])
    op.create_foreign_key(None, 'item', 'service', ['service_id'], ['serviceid'])
    op.create_foreign_key(None, 'item', 'itemtype', ['itemtype_id'], ['itemtypeid'])
    op.create_foreign_key(None, 'item', 'aws', ['aws_id'], ['awsid'])
    op.create_foreign_key(None, 'item', 'area', ['area_id'], ['areaid'])
    op.create_foreign_key(None, 'itemtype', 'normalitemtype', ['normalitemtype_id'], ['normalitemtypeid'])
    op.create_foreign_key(None, 'itemtype', 'aws', ['aws_id'], ['awsid'])
    op.create_foreign_key(None, 'itemtype', 'zbxitemtype', ['zbxitemtype_id'], ['zbxitemtypeid'])
    op.create_foreign_key(None, 'itemtype', 'itemdatatype', ['Itemdatatype_id'], ['itemdatatypeid'])
    op.create_foreign_key(None, 'page', 'user', ['user_id'], ['userid'])
    op.create_foreign_key(None, 'report', 'user', ['user_id'], ['userid'])
    op.create_foreign_key(None, 'reportimg', 'report', ['report_id'], ['reportid'])
    op.create_foreign_key(None, 'reportimg', 'emailschedule', ['emailschedule_id'], ['emailscheduleid'])
    op.create_foreign_key(None, 'series', 'report', ['report_id'], ['reportid'])
    op.create_foreign_key(None, 'series', 'window', ['window_id'], ['windowid'])
    op.create_foreign_key(None, 'series', 'itemtype', ['itemtype_id'], ['itemtypeid'])
    op.create_foreign_key(None, 'service_itemtype', 'service', ['service_id'], ['serviceid'])
    op.create_foreign_key(None, 'service_itemtype', 'itemtype', ['itemtype_id'], ['itemtypeid'])
    op.create_foreign_key(None, 'trigger', 'calculateditem', ['calculateditem_id'], ['calculateditemid'])
    op.drop_column(u'trigger', 'test')
    op.create_foreign_key(None, 'window', 'user', ['user_id'], ['userid'])
    op.create_foreign_key(None, 'window', 'page', ['page_id'], ['pageid'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'window', type_='foreignkey')
    op.drop_constraint(None, 'window', type_='foreignkey')
    op.add_column(u'trigger', sa.Column('test', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'trigger', type_='foreignkey')
    op.drop_constraint(None, 'service_itemtype', type_='foreignkey')
    op.drop_constraint(None, 'service_itemtype', type_='foreignkey')
    op.drop_constraint(None, 'series', type_='foreignkey')
    op.drop_constraint(None, 'series', type_='foreignkey')
    op.drop_constraint(None, 'series', type_='foreignkey')
    op.drop_constraint(None, 'reportimg', type_='foreignkey')
    op.drop_constraint(None, 'reportimg', type_='foreignkey')
    op.drop_constraint(None, 'report', type_='foreignkey')
    op.drop_constraint(None, 'page', type_='foreignkey')
    op.drop_constraint(None, 'itemtype', type_='foreignkey')
    op.drop_constraint(None, 'itemtype', type_='foreignkey')
    op.drop_constraint(None, 'itemtype', type_='foreignkey')
    op.drop_constraint(None, 'itemtype', type_='foreignkey')
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_constraint(None, 'host_itemtype', type_='foreignkey')
    op.drop_constraint(None, 'host_itemtype', type_='foreignkey')
    op.drop_constraint(None, 'host', type_='foreignkey')
    op.drop_constraint(None, 'host', type_='foreignkey')
    op.drop_constraint(None, 'emailschedule', type_='foreignkey')
    op.drop_constraint(None, 'email_report', type_='foreignkey')
    op.drop_constraint(None, 'email_report', type_='foreignkey')
    op.drop_constraint(None, 'email_receiver', type_='foreignkey')
    op.drop_constraint(None, 'email_receiver', type_='foreignkey')
    op.drop_constraint(None, 'aws', type_='foreignkey')
    op.drop_constraint(None, 'area_service', type_='foreignkey')
    op.drop_constraint(None, 'area_service', type_='foreignkey')
    op.drop_constraint(None, 'area_itemtype', type_='foreignkey')
    op.drop_constraint(None, 'area_itemtype', type_='foreignkey')
    op.drop_constraint(None, 'action_trigger', type_='foreignkey')
    op.drop_constraint(None, 'action_trigger', type_='foreignkey')
    ### end Alembic commands ###
