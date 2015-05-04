from monitor import db
from monitor.functions import clock_2_str


region_list ={'ap-southeast-1':'Asia Pacific (Singapore) Region', \
    'IN':'Asia Pacific (Singapore) Region', \
    'AP':'Asia Pacific (Singapore) Region', \
    'APS1':'Asia Pacific (Singapore) Region', \
    'JP':'Asia Pacific (Tokyo) Region', \
    'APN1':'Asia Pacific (Tokyo) Region',\
    'ap-northeast-1':'Asia Pacific (Tokyo) Region', \
    'AU':'Asia Pacific (Sydney) Region', \
    'APS2':'Asia Pacific (Sydney) Region', \
    'ap-southeast-2':'Asia Pacific (Sydney) Region',\
    'EU':'EU (Ireland) Region', \
    'eu-west-1':'EU (Ireland) Region', \
    'SA':'South America (Sao Paulo) Region', \
    'SAE1':'South America (Sao Paulo) Region', \
    'sa-east-1':'South America (Sao Paulo) Region', \
    'US':'US East (Northern Virginia) Region', \
    'us-east-1': 'US East (Northern Virginia) Region', \
    'EUC1':'EU (Frankfurt) Region',\
    'eu-central-1':'EU (Frankfurt) Region',\
    'USW1':'US West (Northern California) Region', \
    'us-west-1':'US West (Northern California) Region', \
    'USW2':'US West (Oregon) Region', \
    'us-west-2':'US West (Oregon) Region'}

DEFAULT_REGION = 'US'

pre_saved_servicename = {'DataTransfer':'Bandwidth'}

TO_TIME_FORMAT = '%B %Y'


class awsservice(db.Model):
    """docstring for awsservice"""

    awsserviceid = db.Column(db.BigInteger, primary_key=True)
    productcode = db.Column(db.String(128))
    productname = db.Column(db.String(128))
    billingrows = db.relationship('billingrow', backref='awsservice', \
        lazy='dynamic')

    def __init__(self, productcode, productname):
        if productcode is None or productname is None:
            raise Exception('Invalid input error in awsservice constructor')
        self.productcode = productcode
        self.productname = productname

    def fee_of_time(self, clock, tmp_linkedaccount=None):
        if clock is None:
            raise Exception('Invalid input in "awsservice.fee_of_time"')

        tmp_arr = db.session.query(db.func.sum(billingrow.totalcost)\
            .label('total')).filter_by(awsservice=self, \
            linkedaccount=tmp_linkedaccount, billingperiodstartdate=clock).all()
        return tmp_arr[0][0] if len(tmp_arr) > 0 else 0

    def build_list(self, clock, tmp_linkedaccount=None):
        if clock is None:
            raise Exception('Invalid input in "awsservice.build_list"')
        tmp_billingrows = self.billingrows.filter_by(\
            linkedaccount=tmp_linkedaccount, billingperiodstartdate=clock).all()
        result = {}
        result['Total'] = 0
        result['region_info'] = {}
        tmp_result = result['region_info']
        tmp_dict = None
        for row in tmp_billingrows:
            result['Total'] += row.totalcost
            tmp_usagetype = row.usagetype
            tmp_services = None
            region_name = None
            if tmp_usagetype is None:
                # print row.itemdescription
                region_name = DEFAULT_REGION
                tmp_services = self.productname
            else:
                tmp_usagetype_split_arr = tmp_usagetype.split('-')
                tmp_header1 = tmp_usagetype_split_arr[0]
                tmp_header2 = None if len(tmp_usagetype_split_arr) < 3 \
                            else '-'.join(tmp_usagetype_split_arr[0:3])
                if tmp_header1 in region_list:
                    region_name = tmp_header1
                    tmp_services = tmp_usagetype_split_arr[1]
                elif tmp_header2 in region_list:
                    region_name = tmp_header2
                    tmp_services = tmp_usagetype_split_arr[3]
                else:
                    region_name = DEFAULT_REGION
                    tmp_services = tmp_usagetype_split_arr[0]

                if row.apioperation is not None:
                    tmp_services = row.apioperation.apioperationname

                if tmp_services in pre_saved_servicename:
                    tmp_services = pre_saved_servicename[tmp_services]
                else:
                    tmp_services = self.productname + tmp_services

            if region_list[region_name] not in tmp_result:
                tmp_result[region_list[region_name]] = {}
                tmp_result[region_list[region_name]]['Total'] = row.totalcost
                tmp_result[region_list[region_name]]['services'] = {}
            else:
                tmp_result[region_list[region_name]]['Total'] += row.totalcost

            # print tmp_result[region_list[region_name]]['services']
            if tmp_services not in tmp_result[region_list[region_name]]\
                    ['services']:
                tmp_result[region_list[region_name]]['services'][tmp_services]\
                 = {}
                tmp_result[region_list[region_name]]['services'][tmp_services]\
                ['Total'] = row.totalcost
                tmp_result[region_list[region_name]]['services'][tmp_services]\
                ['array'] = []
                # print tmp_services
            else:
                tmp_result[region_list[region_name]]['services'][tmp_services]\
                ['Total'] += row.totalcost

            tmp_result[region_list[region_name]]['services'][tmp_services]\
            ['array'].append([row.itemdescription, row.usagequantity, row.totalcost])

        return result


class billingtime(db.Model):
    """docstring for bllingtime"""

    billingtimeid = db.Column(db.BigInteger, primary_key=True)
    billingperiodstartdate = db.Column(db.BigInteger)
    billingperiodenddate = db.Column(db.BigInteger)
    billingrows = db.relationship('billingrow', backref='billingtime', lazy=\
        'dynamic')

    def __init__(self, start_date, end_date):
        if start_date is None or end_date is None:
            raise Exception('Invalid input in billingtime constructor')

        self.billingperiodstartdate = start_date
        self.billingperiodenddate = end_date

    @classmethod
    def get_all_timestr(cls):
        result = []
        for bt in billingtime.query.order_by(cls.billingperiodstartdate.desc())\
            .all():
            clock = bt.billingperiodstartdate
            time_str = clock_2_str(clock, TO_TIME_FORMAT)
            if time_str is not None:
                result.append(time_str)

        return result


        



class linkedaccount(db.Model):
    """docstring for linkedaccount"""

    linkedaccountid = db.Column(db.BigInteger, primary_key=True, \
        autoincrement=False)
    linkedaccountname = db.Column(db.String(128))
    taxationaddress = db.Column(db.String(256))
    billingrows = db.relationship('billingrow', backref='linkedaccount', \
        lazy='dynamic')


    def __init__(self, linkedaccountid, linkedaccountname, taxationaddress):
        if linkedaccountid is None or linkedaccountname is None:
            raise Exception('Invalid input in linkedaccount constructor')

        self.linkedaccountid = linkedaccountid
        self.linkedaccountname = linkedaccountname
        self.taxationaddress = taxationaddress

    def fee_of_time(self, clock):
        if clock is None:
            raise Exception('Invalid input in "linkedaccount.fee_of_time"')
        tmp_arr = db.session.query(db.func.sum(billingrow.totalcost)\
            .label('total')).filter_by(\
            linkedaccount=self, billingperiodstartdate=clock).all()
        return tmp_arr[0][0] if len(tmp_arr) > 0 else 0

    def build_list(self,clock):
        if clock is None:
            raise Exception('Invalid input in "linkedaccount.build_list"')

        result = {}
        result['Total'] = self.fee_of_time(clock)

        result['by_services'] = {}
        for s in awsservice.query.all():
            tmp_r = s.build_list(clock, self)
            if len(tmp_r['region_info']) > 0:
                result['by_services'][s.productname] = tmp_r

        return result


class payeraccount(db.Model):
    """docstring for payeraccount"""
    
    payeraccountid = db.Column(db.BigInteger, primary_key=True, \
        autoincrement=False)
    payeraccountname = db.Column(db.String(128))
    payerponumber = db.Column(db.BigInteger)
    billingrows = db.relationship('billingrow', backref='payeraccount', \
        lazy='dynamic')


    def __init__(self, payeraccountid, payeraccountname, payerponumber):
        if payeraccountid is None or payeraccountname is None:
            raise Exception('Invalid input in payeraccount constructor')

        self.payeraccountid = payeraccountid
        self.payeraccountname = payeraccountname
        self.payerponumber = payerponumber

    def fee_of_time(self, clock, tmp_linkedaccount=None):
        if clock is None:
            raise Exception('Invalid input in payeraccount.fee_of_time')
        tmp_arr = db.session.query(db.func.sum(billingrow.totalcost)\
            .label('total')).filter_by(payeraccount=self,\
            linkedaccount=tmp_linkedaccount, billingperiodstartdate=clock).all()
        return tmp_arr[0][0] if len(tmp_arr) > 0 else 0

class apioperation(db.Model):
    """docstring for apioperation"""

    apioperationid = db.Column(db.BigInteger, primary_key=True)
    apioperationname = db.Column(db.String(128))
    billingrows = db.relationship('billingrow', backref='apioperation', \
        lazy='dynamic')


    def __init__(self, apioperationname):
        if apioperationname is None:
            raise Exception('Invalid input in apioperation constructor')
        self.apioperationname = apioperationname

class invoice(db.Model):
    """docstring for invoice"""

    invoiceid = db.Column(db.BigInteger, primary_key=True, \
        autoincrement=False)
    billingrows = db.relationship('billingrow', backref='invoice', \
        lazy='dynamic')

    def __init__(self, invoiceid):
        if invoiceid is None:
            raise Exception('Invalid input in invoice constructor')
        self.invoiceid = invoiceid

class availablezone(db.Model):
    """docstring for availablezone"""

    availablezoneid = db.Column(db.BigInteger, primary_key=True)
    regionname = db.Column(db.String(128))
    billingrows = db.relationship('billingrow',backref='availablezone', \
        lazy='dynamic')



    def __init__(self, regionname):

        self.regionname = regionname
        
    @classmethod
    def get_region_name_from_usagetype(cls, tmp_usagetype):
        region_name = None

        if tmp_usagetype is None or tmp_usagetype == '':
            # print row.itemdescription
            region_name = DEFAULT_REGION
        else:
            tmp_usagetype_split_arr = tmp_usagetype.split('-')
            tmp_header1 = tmp_usagetype_split_arr[0]
            tmp_header2 = None if len(tmp_usagetype_split_arr) < 3 \
                        else '-'.join(tmp_usagetype_split_arr[0:3])
            if tmp_header1 in region_list:
                region_name = tmp_header1
            elif tmp_header2 in region_list:
                region_name = tmp_header2
            else:
                region_name = DEFAULT_REGION

        return region_list[region_name]

    def fee_of_time(self, clock, tmp_linkedaccount=None):
        tmp_arr = db.session.query(db.func.sum(billingrow.totalcost)\
            .label('total')).filter_by(availablezone=self,\
            linkedaccount=tmp_linkedaccount, billingperiodstartdate=clock).all()
        return tmp_arr[0][0] if len(tmp_arr) > 0 else 0


class billingrow(db.Model):
    """docstring for billingrow"""

    billingrowid = db.Column(db.BigInteger, primary_key=True)
    billingperiodstartdate = db.Column(db.BigInteger)
    billingperiodenddate = db.Column(db.BigInteger)
    invoicedate = db.Column(db.BigInteger)
    sellerofrecord = db.Column(db.String(128))
    usagetype = db.Column(db.String(128))
    rateid = db.Column(db.BigInteger)
    itemdescription = db.Column(db.String(256))
    usagestartdate = db.Column(db.BigInteger)
    usageenddate = db.Column(db.BigInteger)
    usagequantity = db.Column(db.Float)
    blendedrate = db.Column(db.Float)
    currencycode = db.Column(db.String(64))
    costbeforetax = db.Column(db.Float)
    credits = db.Column(db.Float)
    taxamount = db.Column(db.Float)
    taxtype = db.Column(db.String(128))
    totalcost = db.Column(db.Float)

    invoice_id = db.Column(db.BigInteger, db.ForeignKey('invoice.invoiceid'))
    apioperation_id = db.Column(db.BigInteger, \
        db.ForeignKey('apioperation.apioperationid'))
    payeraccount_id = db.Column(db.BigInteger, \
        db.ForeignKey('payeraccount.payeraccountid'))
    linkedaccount_id = db.Column(db.BigInteger, \
        db.ForeignKey('linkedaccount.linkedaccountid'))
    awsservice_id = db.Column(db.BigInteger, \
        db.ForeignKey('awsservice.awsserviceid'))
    availablezone_id = db.Column(db.BigInteger, \
        db.ForeignKey('availablezone.availablezoneid'))
    billingtime_id = db.Column(db.BigInteger, \
        db.ForeignKey('billingtime.billingtimeid'))


    def __init__(self, billingperiodstartdate,\
        billingperiodenddate,\
        invoicedate,\
        sellerofrecord,\
        usagetype,\
        rateid,\
        itemdescription,\
        usagestartdate,\
        usageenddate,\
        usagequantity,\
        blendedrate,\
        currencycode,\
        costbeforetax,\
        credits,\
        taxamount,\
        taxtype,\
        totalcost,\
        tmp_invoice=None,\
        tmp_apioperation=None,\
        tmp_payeraccount=None,\
        tmp_linkedaccount=None,\
        tmp_awsservice=None,
        tmp_availablezone=None,
        tmp_billingtime=None):
        if billingperiodstartdate is None or billingperiodenddate is None or \
            invoicedate is None or itemdescription is None or usagequantity is \
            None or totalcost is None:
            raise Exception('Invalid input in billingrow constructor')
        self.billingperiodstartdate = billingperiodstartdate
        self.billingperiodenddate = billingperiodenddate
        self.invoicedate = invoicedate
        self.sellerofrecord = sellerofrecord
        self.usagetype = usagetype
        self.rateid = rateid
        self.itemdescription = itemdescription
        self.usagestartdate = usagestartdate
        self.usageenddate = usageenddate
        self.usagequantity = usagequantity
        self.blendedrate = blendedrate
        self.currencycode = currencycode
        self.costbeforetax = costbeforetax
        self.credits = credits
        self.taxamount = taxamount
        self.taxtype = taxtype
        self.totalcost = totalcost
        self.invoice = tmp_invoice
        self.apioperation = tmp_apioperation
        self.payeraccount = tmp_payeraccount
        self.linkedaccount = tmp_linkedaccount
        self.awsservice = tmp_awsservice
        self.availablezone = tmp_availablezone
        self.billingtime = tmp_billingtime


    @classmethod
    def get_billstart_month(cls):
        result = []
        for x in cls.query.group_by(billingrow.billingperiodstartdate).all():
            clock = x.billingperiodstartdate
            time_str = clock_2_str(clock, TO_TIME_FORMAT)
            if time_str is not None:
                result.append(time_str)

        return result
