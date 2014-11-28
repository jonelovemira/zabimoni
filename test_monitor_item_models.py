#! flask/bin/python

from monitor.item.models import Normalitemtype,Area,Service,Host,Itemtype,Zbxitemtype
from monitor import db


def add_remove_test(o,it):
	otmp = o.add_itemtype(it)
	if otmp != None:
		db.session.add(otmp)
		db.session.commit()
	print o.itemtypes.all()

	otmp = o.rm_itemtype(it)
	if otmp != None:
		db.session.add(otmp)
		db.session.commit()
	print o.itemtypes.all()


it = Itemtype.query.first()

a = Area.query.first()
add_remove_test(a,it)

s = Service.query.first()
add_remove_test(s,it)

h = Host.query.first()
add_remove_test(h,it)


nit = Normalitemtype()
db.session.add(nit)
db.session.commit()
print Normalitemtype.query.all()
try:
    num_rows_deleted = db.session.query(Normalitemtype).delete()
    db.session.commit()
except:
    db.session.rollback()
print Normalitemtype.query.all()

zit = Zbxitemtype()
db.session.add(zit)
db.session.commit()

it.zit = zit
db.session.add(it)
db.session.commit()
print it.zit
zit.itemtypes.remove(it)
db.session.add(zit)
db.session.commit()
print it.zit


print Zbxitemtype.query.all()
try:
    num_rows_deleted = db.session.query(Zbxitemtype).delete()
    db.session.commit()
except:
    db.session.rollback()
print Zbxitemtype.query.all()