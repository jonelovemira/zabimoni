from monitor import db
# from monitor.chart.models import Series
# from monitor.item.models import Item


class Attr(db.Model):
	attrid = db.Column(db.Integer,primary_key=True)
	attrname = db.Column(db.String(80))
	attrvalue = db.Column(db.String(80))

	displaytablerow_id = db.Column(db.Integer,db.ForeignKey('displaytablerow.displaytablerowid'))
	chartconfig_id = db.Column(db.Integer,db.ForeignKey('chartconfig.chartconfigid'))
	operation_id = db.Column(db.Integer,db.ForeignKey('operation.operationid'))

	def __init__(self,attrname,attrvalue,displaytablerow=None,chartconfig=None,operation=None):
		self.attrname = attrname
		self.attrvalue = attrvalue
		self.displaytablerow = displaytablerow
		self.chartconfig = chartconfig
		self.operation = operation

	def __repr__(self):
		return '<Attr key: %r value: %r>' % (attrname,attrvalue)


# series_item = db.Table('series_item',
# 				db.Column('series_id',db.Integer,db.ForeignKey('series.seriesid')),
# 				db.Column('item_id',db.Integer,db.ForeignKey('item.itemid')))


