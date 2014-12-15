from sqlalchemy import create_engine, MetaData, Table,select
from sqlalchemy import Column,Integer, String, Text ,DateTime, Float,BigInteger
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func,union
# from monitor import db

engine = create_engine('mysql://zabbix:zabbix@localhost/zabbix')
Base = declarative_base(engine)

class Zabbixhistory(Base):
        __tablename__ = 'history'
        itemid = Column('itemid',Integer,primary_key=True)
        clock = Column('clock',BigInteger,primary_key=True)
        value = Column('value',Float)
        ns = Column('ns',Integer)
        
        def __repr__(self):
            return "<zabbix history itemid - %s value - %s at %s>" % (self.itemid,self.value,self.clock)


class Zabbixhistoryuint(Base):
        __tablename__ = 'history_uint'
        itemid = Column('itemid',Integer,primary_key=True)
        clock = Column('clock',BigInteger,primary_key=True)
        value = Column('value',Float)
        ns = Column('ns',Integer)

        def __repr__(self):
            return "<zabbix history_uint itemid - %s value - %s at %s>" % (self.itemid,self.value,self.clock)

def zabbix_history(engine,itemid_list,ground):


    

    #----------------------------------------------------------------------
    # def loadSession():
    #     """"""  
    #     metadata = MetaData(engine)
    #     Session = sessionmaker(bind=engine)
    #     session = Session()
    #     return session

    def gen_history_select_object(item,ground):
        s1 = select(    [Zabbixhistory.itemid,\
                        func.count(Zabbixhistory.itemid).label('count'),\
                        func.avg(Zabbixhistory.value).label('avg'),\
                        func.max(Zabbixhistory.value).label('max'),\
                        func.min(Zabbixhistory.value).label('min'),\
                        func.floor((Zabbixhistory.clock)/ground).label('minute') ]). \
            where(Zabbixhistory.itemid == item). \
            group_by('minute') 

        return s1

    def gen_history_uint_select_object(item,ground):
        s1 = select(    [Zabbixhistoryuint.itemid,\
                        func.count(Zabbixhistoryuint.itemid).label('count'),\
                        func.avg(Zabbixhistoryuint.value).label('avg'),\
                        func.max(Zabbixhistoryuint.value).label('max'),\
                        func.min(Zabbixhistoryuint.value).label('min'),\
                        func.floor((Zabbixhistoryuint.clock)/ground).label('minute') ]). \
            where(Zabbixhistoryuint.itemid == item). \
            group_by('minute') 

        return s1

    def get_itemlist_history(itemid_list,ground):

        s = []

        for item in itemid_list:
            tmp_s = gen_history_select_object(item,ground)
            s.append(tmp_s)

        u = union(*s).alias('Newtable')

        session = loadSession()

        res = session.query(func.sum(u.c.count).label('count'),\
                      func.avg(u.c.avg).label('avg'),\
                      func.max(u.c.max).label('max'),\
                      func.min(u.c.min).label('min'),\
                      u.c.minute).group_by(u.c.minute).all()
        session.close()
        return res


    def get_itemlist_history_uint(itemid_list,ground):

        s = []

        for item in itemid_list:
            tmp_s = gen_history_uint_select_object(item,ground)
            s.append(tmp_s)

        u = union(*s).alias('Newtable')

        session = loadSession()

        res = session.query(func.sum(u.c.count).label('count'),\
                      func.avg(u.c.avg).label('avg'),\
                      func.max(u.c.max).label('max'),\
                      func.min(u.c.min).label('min'),\
                      u.c.minute).group_by(u.c.minute).all()
        session.close()
        return res

    def get_history(itemid_list,ground):

        return get_itemlist_history(itemid_list,ground) + get_itemlist_history_uint(itemid_list,ground)

    return get_history(itemid_list,ground)


def zabbix_update_history(engine,itemid_list,ground,time_till,time_since):

    def gen_history_select_object(item,ground,time_till,time_since):
        s1 = select(    [Zabbixhistory.itemid,\
                        func.count(Zabbixhistory.itemid).label('count'),\
                        func.avg(Zabbixhistory.value).label('avg'),\
                        func.max(Zabbixhistory.value).label('max'),\
                        func.min(Zabbixhistory.value).label('min'),\
                        func.floor((Zabbixhistory.clock)/ground).label('minute') ]). \
            where(Zabbixhistory.itemid == item).\
            where(Zabbixhistory.clock >= time_since ).\
            where(Zabbixhistory.clock <= time_till). \
            group_by('minute') 

        # print s1

        return s1

    def gen_history_uint_select_object(item,ground,time_till,time_since):
        s1 = select(    [Zabbixhistoryuint.itemid,\
                        func.count(Zabbixhistoryuint.itemid).label('count'),\
                        func.avg(Zabbixhistoryuint.value).label('avg'),\
                        func.max(Zabbixhistoryuint.value).label('max'),\
                        func.min(Zabbixhistoryuint.value).label('min'),\
                        func.floor((Zabbixhistoryuint.clock)/ground).label('minute') ]). \
            where(Zabbixhistoryuint.itemid == item ).\
            where(Zabbixhistoryuint.clock >= time_since ).\
            where(Zabbixhistoryuint.clock <= time_till). \
            group_by('minute') 

        return s1

    def get_itemlist_history(itemid_list,ground,time_till,time_since):

        s = []

        for item in itemid_list:
            tmp_s = gen_history_select_object(item,ground,time_till,time_since)
            s.append(tmp_s)

        u = union(*s).alias('Newtable')

        session = loadSession()

        res = session.query(func.sum(u.c.count).label('count'),\
                      func.avg(u.c.avg).label('avg'),\
                      func.max(u.c.max).label('max'),\
                      func.min(u.c.min).label('min'),\
                      u.c.minute).group_by(u.c.minute).all()
        session.close()
        return res


    def get_itemlist_history_uint(itemid_list,ground,time_till,time_since):

        s = []

        for item in itemid_list:
            tmp_s = gen_history_uint_select_object(item,ground,time_till,time_since)
            s.append(tmp_s)

        u = union(*s).alias('Newtable')

        session = loadSession()

        res = session.query(func.sum(u.c.count).label('count'),\
                      func.avg(u.c.avg).label('avg'),\
                      func.max(u.c.max).label('max'),\
                      func.min(u.c.min).label('min'),\
                      u.c.minute).group_by(u.c.minute).all()
        session.close()
        return res

    def get_history(itemid_list,ground,time_till,time_since):

        return get_itemlist_history(itemid_list,ground,time_till,time_since) + get_itemlist_history_uint(itemid_list,ground,time_till,time_since)

    return get_history(itemid_list,ground,time_till,time_since)





class Zabbixhosts(Base):
    __tablename__ = 'hosts'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return "<zabbix host name - %s hostid - %s>" % (self.name,self.hostid)


class Zabbixitems(Base):
    __tablename__ = 'items'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return "<zabbix item name - %s itemid - %s>" % (self.name,self.itemid)

class Zabbixhostgroup(Base):
    __tablename__ = 'groups'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return "<zabbix group name - %s groupid - %s>" % (self.name,self.groupid)

class Zabbixinterface(Base):
    __tablename__ = 'interface'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return "<zabbix interface hostid - %s ip - %s>" % (self.hostid,self.ip)

class Zabbixapplication(Base):
    __tablename__ = 'applications'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return '<zabbix applications applicationid %s name - %s>' % (self.applicationid,self.name)

class Zabbixitemapplication(Base):
    __tablename__ = 'items_applications'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return '<zabbix items_applications itemappid %s>' % (self.itemappid)

class Zabbixfunctions(Base):
    __tablename__ = 'functions'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return '<zabbix functions %s>' % (self.function)

class Zabbixtriggers(Base):
    __tablename__ = 'triggers'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return '<zabbix triggers %s>' % (self.expression)

class Zabbixactions(Base):
    __tablename__ = 'actions'
    __table_args__ = {'autoload':True}
    def __repr__(self):
        return '<zabbix actions %s>' % (self.name)


def loadSession():
    session = None
    for attempt in range(3):
        try:
            metadata = Base.metadata
            Session = sessionmaker(bind=engine)
            session = Session()
            session.query(Zabbixhistory).first()
            return session
        except Exception, e:
            if session != None:
                session.close()
            attempt += 1
            if attempt == 3:
                raise Exception('bind zabbix database error')



# if __name__ == "__main__":
#     session = loadSession()
#     res = session.query(Zabbixitemapplication).all()
#     # print res[1].title
#     for row in res:
#         print row


# def zabbix_hosts(engine):
#     engine = engine #create_engine('mysql://root:root@localhost/zabbix')
#     Base = declarative_base(engine) 




# if __name__ == "__main__":
#     engine = create_engine('mysql://root:root@localhost/zabbix')
#     itemlist = ['28373','28375']
#     ground = 60
#     print zabbix(engine,itemlist,ground)