from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
series_item = Table('series_item', pre_meta,
    Column('series_id', INTEGER(display_width=11)),
    Column('item_id', INTEGER(display_width=11)),
)

series = Table('series', post_meta,
    Column('seriesid', Integer, primary_key=True, nullable=False),
    Column('seriesname', String(length=1000)),
    Column('index', Integer),
    Column('area_id', String(length=1000)),
    Column('service_id', String(length=1000)),
    Column('host_id', String(length=1000)),
    Column('aws_id', String(length=1000)),
    Column('itemtype_id', Integer),
    Column('window_id', Integer),
    Column('report_id', Integer),
    Column('r', String(length=1000)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['series_item'].drop()
    post_meta.tables['series'].columns['r'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['series_item'].create()
    post_meta.tables['series'].columns['r'].drop()
