"""empty message

Revision ID: 538a5fc30e2a
Revises: 432d75e5c300
Create Date: 2015-02-05 01:26:27.395548

"""

# revision identifiers, used by Alembic.
revision = '538a5fc30e2a'
down_revision = '432d75e5c300'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('selectedmetrics',
    sa.Column('selectedmetricsid', sa.Integer(), nullable=False),
    sa.Column('window_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['window_id'], ['window.windowid'], ),
    sa.PrimaryKeyConstraint('selectedmetricsid')
    )
    op.create_table('chartconfig',
    sa.Column('chartconfigid', sa.Integer(), nullable=False),
    sa.Column('window_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['window_id'], ['window.windowid'], ),
    sa.PrimaryKeyConstraint('chartconfigid')
    )
    op.create_table('option',
    sa.Column('optionid', sa.Integer(), nullable=False),
    sa.Column('optionname', sa.String(length=80), nullable=True),
    sa.Column('selectedmetrics_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['selectedmetrics_id'], ['selectedmetrics.selectedmetricsid'], ),
    sa.PrimaryKeyConstraint('optionid')
    )
    op.create_table('displaytable',
    sa.Column('displaytableid', sa.Integer(), nullable=False),
    sa.Column('displaytablename', sa.String(length=80), nullable=True),
    sa.Column('option_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['option_id'], ['option.optionid'], ),
    sa.PrimaryKeyConstraint('displaytableid')
    )
    op.create_table('displaytablerow',
    sa.Column('displaytablerowid', sa.Integer(), nullable=False),
    sa.Column('displaytable_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['displaytable_id'], ['displaytable.displaytableid'], ),
    sa.PrimaryKeyConstraint('displaytablerowid')
    )
    op.create_table('attr',
    sa.Column('attrid', sa.Integer(), nullable=False),
    sa.Column('attrname', sa.String(length=80), nullable=True),
    sa.Column('attrvalue', sa.String(length=80), nullable=True),
    sa.Column('displaytablerow_id', sa.Integer(), nullable=True),
    sa.Column('chartconfig_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chartconfig_id'], ['chartconfig.chartconfigid'], ),
    sa.ForeignKeyConstraint(['displaytablerow_id'], ['displaytablerow.displaytablerowid'], ),
    sa.PrimaryKeyConstraint('attrid')
    )
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
    op.create_foreign_key(None, 'window', 'user', ['user_id'], ['userid'])
    op.create_foreign_key(None, 'window', 'page', ['page_id'], ['pageid'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'window', type_='foreignkey')
    op.drop_constraint(None, 'window', type_='foreignkey')
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
    op.drop_table('attr')
    op.drop_table('displaytablerow')
    op.drop_table('displaytable')
    op.drop_table('option')
    op.drop_table('chartconfig')
    op.drop_table('selectedmetrics')
    ### end Alembic commands ###