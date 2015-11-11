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
        index_date_map = []
        index = 0
        for itvd in self.intervaldatas.order_by(intervaldata.timefrom).all():
            date = clock_2_str(itvd.timefrom, DATE_FORMAT)
            if not result.has_key(date):
                result[date] = {}
                index_date_map.append(date)

            result[date][itvd.displayname] = itvd.sumv

        order_result = []
        for di in xrange(len(index_date_map)):
            tmp = {
                "date" : index_date_map[di],
                "data" : result[index_date_map[di]]
            }
            order_result.append(tmp)
        return order_result

class region(db.Model):
    """docstring for region"""
    regionid = db.Column(db.Integer, primary_key=True)
    regionshort = db.Column(db.String(128), nullable=False)
    regionlong = db.Column(db.String(128), nullable=False)
    counts = db.relationship("count", backref="region", \
        lazy="dynamic")
    def __init__(self, regionshort, regionlong):
        self.regionshort = regionshort
        self.regionlong = regionlong


class counttype(db.Model):
    """docstring for counttype """
    counttypeid = db.Column(db.Integer, primary_key=True)
    counttypename = db.Column(db.String(128), nullable=False)
    counts = db.relationship("count", backref="counttype", \
        lazy="dynamic")
    def __init__(self, counttypename):
        self.counttypename = counttypename

class count(db.Model):
    """docstring for count"""
    countid = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    clock = db.Column(db.BigInteger, nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey("region.regionid"))
    counttype_id = db.Column(db.Integer, db.ForeignKey("counttype.counttypeid"))

    def __init__(self, value, clock, region, counttype):
        self.value = value
        self.clock = clock
        self.region = region
        self.counttype = counttype

    @classmethod
    def get_all_month_str(cls):
        result = []
        for c in cls.query.order_by(count.clock).all():
            month_str = clock_2_str(int(c.clock), MONTH_FORMAT)
            if month_str not in result:
                result.append(month_str)
        return result




        

        
            
        