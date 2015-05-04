#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import csv, inspect, os, sys, traceback

currentdir = os.path.dirname(os.path.abspath(\
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config

from monitor.billing.models import *
from monitor import db
from monitor.functions import str_2_clock

INVOICEDATE = 'InvoiceDate'
PRODUCTCODE = 'ProductCode'
INVOICEID = 'InvoiceID'
PAYERACCOUNTID = 'PayerAccountId'
LINKEDACCOUNTID = 'LinkedAccountId'
RECORDTYPE = 'RecordType'
RECORDID = 'RecordID'
BILLINGPERIODSTARTDATE = 'BillingPeriodStartDate'
BILLINGPERIODENDDATE = 'BillingPeriodEndDate'
INVOICEDATE = 'InvoiceDate'
PAYERACCOUNTNAME = 'PayerAccountName'
LINKEDACCOUNTNAME = 'LinkedAccountName'
TAXATIONADDRESS = 'TaxationAddress'
PAYERPONUMBER = 'PayerPONumber'
PRODUCTCODE = 'ProductCode'
PRODUCTNAME = 'ProductName'
SELLEROFRECORD = 'SellerOfRecord'
USAGETYPE = 'UsageType'
OPERATION = 'Operation'
RATEID = 'RateId'
ITEMDESCRIPTION = 'ItemDescription'
USAGESTARTDATE = 'UsageStartDate'
USAGEENDDATE = 'UsageEndDate'
USAGEQUANTITY = 'UsageQuantity'
BLENDEDRATE = 'BlendedRate'
CURRENCYCODE = 'CurrencyCode'
COSTBEFORETAX = 'CostBeforeTax'
CREDITS = 'Credits'
TAXAMOUNT = 'TaxAmount'
TAXTYPE = 'TaxType'
TOTALCOST = 'TotalCost'

TIME_FORMAT = "%Y/%m/%d %H:%M:%S"


class CsvToDbRecord():
    """docstring for CsvToDbRecord"""

    def __init__(self, filepath):
        if filepath is None:
            raise Exception('Invalid input in CsvToDbRecord.constructor')
        self.filepath = filepath

    def read_save_billing_records(self):
        with open(self.filepath, 'rb') as f:
            reader = csv.reader(f)
            headers = None
            count = 0
            for row in reader:
                if count is 0:
                    headers = row
                    count += 1
                else:
                    if row[headers.index(INVOICEDATE)] != '' and \
                        row[headers.index(PRODUCTCODE)] != '':
                        try:
                            self.build_db_record_from_row(row, headers)

                        except Exception, e:
                            traceback.print_exc(file=sys.stdout)
                            print str(e)
                            break

    def parse_empty_str_2_none(self, tmp_str):

        return None if tmp_str == '' else tmp_str

    def build_db_record_from_row(self, row, headers):
        if row is None or headers is None:
            raise Exception('Invalid input in ' + \
                'CsvToDbRecord.build_db_record_from_row')

        # invoice
        tmp_invoiceid = row[headers.index(INVOICEID)]
        assert tmp_invoiceid != ''
        tmp_invoice = invoice.query.get(tmp_invoiceid)
        if tmp_invoiceid != 'Estimated':
            if tmp_invoice is None:
                tmp_invoice = invoice(tmp_invoiceid)
                db.session.add(tmp_invoice)

        tmp_billingstarttime = row[headers.index(BILLINGPERIODSTARTDATE)]
        tmp_billingendtime = row[headers.index(BILLINGPERIODENDDATE)]
        assert tmp_billingstarttime != ''
        assert tmp_billingendtime != ''
        start_clock = str_2_clock(tmp_billingstarttime, TIME_FORMAT)
        end_clock = str_2_clock(tmp_billingendtime, TIME_FORMAT)
        assert start_clock != None
        assert end_clock != None
        tmp_billtingtime = billingtime.query.filter_by(billingperiodstartdate=\
            start_clock, billingperiodenddate=end_clock).first()
        if tmp_billtingtime is None:
            tmp_billtingtime = billingtime(start_clock,end_clock)
            db.session.add(tmp_billtingtime)

        # payeraccount
        tmp_payeraccountid = row[headers.index(PAYERACCOUNTID)]
        assert tmp_payeraccountid != ''
        tmp_payeraccount = payeraccount.query.get(tmp_payeraccountid)
        if tmp_payeraccount is None:
            tmp_payeraccountname = row[headers.index(PAYERACCOUNTNAME)]
            tmp_payerponumber = self.parse_empty_str_2_none(\
                row[headers.index(PAYERPONUMBER)])
            assert tmp_payeraccountname != ''
            tmp_payeraccount = payeraccount(tmp_payeraccountid, \
                tmp_payeraccountname, tmp_payerponumber)
            db.session.add(tmp_payeraccount)

        # linkedaccount
        tmp_linkedaccountid = row[headers.index(LINKEDACCOUNTID)]
        tmp_linkedaccount = None
        if tmp_linkedaccountid != '':
            tmp_linkedaccount = linkedaccount.query.get(tmp_linkedaccountid)
            if tmp_linkedaccount is None:
                tmp_linkedaccountname = row[headers.index(LINKEDACCOUNTNAME)]
                assert tmp_linkedaccountname != ''
                tmp_taxationaddress = self.parse_empty_str_2_none(\
                    row[headers.index(TAXATIONADDRESS)])
                tmp_linkedaccount = linkedaccount(tmp_linkedaccountid, \
                    tmp_linkedaccountname, tmp_taxationaddress)
                db.session.add(tmp_linkedaccount)




        # awsservice
        tmp_productcode = row[headers.index(PRODUCTCODE)]
        tmp_productname = row[headers.index(PRODUCTNAME)]
        assert tmp_productname != '' and tmp_productcode != ''
        tmp_awsservice = awsservice.query.\
        filter_by(productcode=tmp_productcode).first()
        if tmp_awsservice is None:
            tmp_awsservice = awsservice(tmp_productcode, tmp_productname)
            db.session.add(tmp_awsservice)

        # apioperation
        tmp_operationname = row[headers.index(OPERATION)]
        tmp_apioperation = None
        if tmp_operationname != '':
            tmp_apioperation = apioperation.query.\
            filter_by(apioperationname=tmp_operationname).first()
            if tmp_apioperation is None:
                tmp_apioperation = apioperation(tmp_operationname)
                db.session.add(tmp_apioperation)

        tmp_usagetype = self.parse_empty_str_2_none(\
            row[headers.index(USAGETYPE)])
        assert tmp_usagetype != ''
        tmp_availablezone = None
        tmp_region_name = availablezone.get_region_name_from_usagetype(\
            tmp_usagetype)
        tmp_availablezone = availablezone.query.filter_by(regionname=\
            tmp_region_name).first()
        if tmp_availablezone is None:
            tmp_availablezone = availablezone(tmp_region_name)
            db.session.add(tmp_availablezone)


        # billingrow
        tmp_billingperiodstartdate = self.parse_empty_str_2_none(\
            row[headers.index(BILLINGPERIODSTARTDATE)]) 
        tmp_billingperiodenddate = self.parse_empty_str_2_none(\
            row[headers.index(BILLINGPERIODENDDATE)])
        tmp_invoicedate = self.parse_empty_str_2_none(\
            row[headers.index(INVOICEDATE)])
        tmp_sellerofrecord = self.parse_empty_str_2_none(\
            row[headers.index(SELLEROFRECORD)])
        tmp_usagetype = self.parse_empty_str_2_none(\
            row[headers.index(USAGETYPE)])
        tmp_rateid = self.parse_empty_str_2_none(\
            row[headers.index(RATEID)])
        tmp_itemdescription = self.parse_empty_str_2_none(\
            row[headers.index(ITEMDESCRIPTION)])
        tmp_usagestartdate = self.parse_empty_str_2_none(\
            row[headers.index(USAGESTARTDATE)])
        tmp_usageenddate = self.parse_empty_str_2_none(\
            row[headers.index(USAGEENDDATE)])
        tmp_usagequantity = self.parse_empty_str_2_none(\
            row[headers.index(USAGEQUANTITY)])
        tmp_blendedrate = self.parse_empty_str_2_none(\
            row[headers.index(BLENDEDRATE)])
        tmp_currencycode = self.parse_empty_str_2_none(\
            row[headers.index(CURRENCYCODE)])
        tmp_costbeforetax = self.parse_empty_str_2_none(\
            row[headers.index(COSTBEFORETAX)])
        tmp_credits = self.parse_empty_str_2_none(\
            row[headers.index(CREDITS)])
        tmp_taxamount = self.parse_empty_str_2_none(\
            row[headers.index(TAXAMOUNT)])
        tmp_taxtype = self.parse_empty_str_2_none(\
            row[headers.index(TAXTYPE)])
        tmp_totalcost = self.parse_empty_str_2_none(\
            row[headers.index(TOTALCOST)])

        assert tmp_billingperiodstartdate != '' and\
                tmp_billingperiodenddate !='' and\
                tmp_invoicedate !='' and\
                tmp_usagestartdate !='' and\
                tmp_usageenddate !='' and \
                tmp_usagequantity !='' and \
                tmp_totalcost != ''

        tmp_bsdc = str_2_clock(tmp_billingperiodstartdate,TIME_FORMAT)
        tmp_br = billingrow.query.filter_by(billingperiodstartdate=tmp_bsdc,\
            invoice=tmp_invoice, apioperation=tmp_apioperation, payeraccount=\
            tmp_payeraccount, linkedaccount=tmp_linkedaccount, awsservice=\
            tmp_awsservice, usagetype=tmp_usagetype, \
            itemdescription=tmp_itemdescription ).first()
        if tmp_br is not None:
            db.session.delete(tmp_br)

        tmp_billingrow = billingrow(str_2_clock(tmp_billingperiodstartdate,\
            TIME_FORMAT),\
            str_2_clock(tmp_billingperiodenddate, TIME_FORMAT) ,\
            str_2_clock(tmp_invoicedate, TIME_FORMAT) ,\
            tmp_sellerofrecord,\
            tmp_usagetype,\
            tmp_rateid,\
            tmp_itemdescription,\
            str_2_clock(tmp_usagestartdate, TIME_FORMAT) ,\
            str_2_clock(tmp_usageenddate, TIME_FORMAT) ,\
            tmp_usagequantity,\
            tmp_blendedrate,\
            tmp_currencycode,\
            tmp_costbeforetax, \
            tmp_credits, \
            tmp_taxamount, \
            tmp_taxtype, \
            tmp_totalcost, \
            tmp_invoice, \
            tmp_apioperation, \
            tmp_payeraccount, \
            tmp_linkedaccount, \
            tmp_awsservice,\
            tmp_availablezone,\
            tmp_billtingtime)

        db.session.add(tmp_billingrow)
        db.session.commit()

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        raise Exception('Need csv file!')
    filename = sys.argv[1]
    print filename
    c2dr = CsvToDbRecord(filename)
    c2dr.read_save_billing_records()