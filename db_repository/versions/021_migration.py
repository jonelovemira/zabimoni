from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
report = Table('report', pre_meta,
    Column('reportid', INTEGER(display_width=11), primary_key=True, nullable=False),
    Column('clock_since', INTEGER(display_width=11)),
    Column('clock_till', INTEGER(display_width=11)),
    Column('scaletype', INTEGER(display_width=11)),
    Column('functiontype', INTEGER(display_width=11)),
    Column('reportname', VARCHAR(length=80)),
    Column('user_id', INTEGER(display_width=11)),
    Column('title', VARCHAR(length=80)),
    Column('discription', VARCHAR(length=200)),
)

emailschedule = Table('emailschedule', post_meta,
    Column('emailscheduleid', Integer, primary_key=True, nullable=False),
    Column('frequency', Integer),
    Column('starttime', String(length=80)),
    Column('subject', String(length=80)),
    Column('timezone', Integer),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['report'].columns['clock_since'].drop()
    pre_meta.tables['report'].columns['clock_till'].drop()
    post_meta.tables['emailschedule'].columns['timezone'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['report'].columns['clock_since'].create()
    pre_meta.tables['report'].columns['clock_till'].create()
    post_meta.tables['emailschedule'].columns['timezone'].drop()
