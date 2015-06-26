from monitor import db
from monitor.functions import clock_2_str

MONTH_FORMAT = '%B %Y'
DATE_FORMAT = '%Y/%m/%d'


class intervaldata(db.Model):
    """docstring for intervaldata"""

    intervaldataid = db.Column(db.Integer, primary_key=True)
    timefrom = db.Column(db.BigInteger, nullable=False)
    timeto = db.Column(db.BigInteger, nullable=False)
    groupname = db.Column(db.String(128), nullable=False)
    itemkey = db.Column(db.String(128), nullable=False)
    displayname = db.Column(db.String(128))
    sumv = db.Column(db.Float)
    odmonth_id = db.Column(db.Integer, db.ForeignKey("odmonth.odmonthid"))

    def __init__(self, timefrom, timeto, groupname, itemkey, displayname,\
         sumv, odmonth):
        self.timefrom = timefrom
        self.timeto = timeto
        self.groupname = groupname
        self.itemkey = itemkey
        self.displayname = displayname
        self.sumv = sumv
        self.odmonth = odmonth

class odmonth(db.Model):
    """docstring for odmonth"""
    odmonthid = db.Column(db.Integer, primary_key=True)
    beginclock = db.Column(db.Integer, unique=True)
    intervaldatas = db.relationship("intervaldata", backref="odmonth", \
        lazy="dynamic")

    def __init__(self, beginclock):

        self.beginclock = beginclock

    @classmethod
    def get_all_timestr(cls):
        result = []
        for bt in cls.query.order_by(cls.beginclock.desc())\
            .all():
            clock = bt.beginclock
            time_str = clock_2_str(clock, MONTH_FORMAT)
            if time_str is not None:
                result.append(time_str)

        return result

    def gen_table_content(self):
        result = {}

        for itvd in self.intervaldatas.all():
            date = clock_2_str(itvd.timefrom, DATE_FORMAT)
            if not result.has_key(date):
                result[date] = {}

            result[date][itvd.displayname] = itvd.sumv

        return result
            
        