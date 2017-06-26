from django.core.management.base import BaseCommand, CommandError

import urllib2
import lxml.html
from lxml.cssselect import CSSSelector
import os
import xlrd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from datetime import datetime

from landlord_registry.models import registration
from map.models import parcel

"""
This utility downloads the latest landlord registry spreadsheet from the
Indianapolis Department of Business and Neighborhood Services (Code Enforcement)
and then looks up each registration number one at a time and scrapes relevant
data into a landlord registration object.

Since Accella, the system that hosts the registration data, is incredibly
stupid and requires javascript we need to scrape with selenium and a headless
browser.

The alterative way to do this would be to brute force the record address space,
which we can do without javascript and hence just with mechanize or urllib2.
The trade off is just in the number of requests - selenium is probably 1/3 the
speed but the total address space is more than 3x as large so selenium wins.

I wrote another tool to brute force record address space, you can see it here:
https://github.com/ChrisHartley/alohomora-landlord-registry/blob/master/scrape-accela.py



The filename of the landlord registry spreadsheet datetime stamped so we need
to access the page linking to it to get the current file name.

As with any scraping project this is a fragile process. It should be easy to
fix when it breaks (eg when they re-organize the BNS website) by just changing
the base URL and CSS selector for the file link but golly wouldn't that be
annoying.

Fixing Accella scraping if that breaks is more annoying and tedious but
essentially the same.

"""



def get_record_html(driver, record_number):
    url = 'https://permitsandcases.indy.gov/CitizenAccess/Cap/CapHome.aspx?module=Licenses&TabName=Licenses&TabList=HOME%7C0%7CPermits%7C1%7CEnforcement%7C2%7CLicenses%7C3%7CHHC%7C4%7CPlanning%7C5%7CCurrentTabIndex%7C3'
    html = ''
    driver.get(url)
    try:
	    element = WebDriverWait(driver, 20).until(
		    EC.presence_of_element_located((By.ID, "ctl00_PlaceHolderMain_generalSearchForm_txtGSPermitNumber"))
	    )
    except:
        print "timeout, saving screenshot"
        driver.save_screenshot('ERROR-loading.png')
    # enter parcel number and click submit
    finally:
        try:
    	    element = WebDriverWait(driver, 20).until(
    		    EC.presence_of_element_located((By.ID, "ctl00_PlaceHolderMain_generalSearchForm_txtGSPermitNumber"))
    	    )
            element.send_keys('LLRR17-000556')
            #driver.find_element_by_id('ctl00_PlaceHolderMain_generalSearchForm_txtGSParcelNo').send_keys('LLRR17-000556')
            driver.find_element_by_id("ctl00_PlaceHolderMain_btnNewSearch").click()
        except:
            driver.execute_script('document.body.style.background = "white"')
            driver.save_screenshot('ERROR-searching.png')
        try:
            element = WebDriverWait(driver, 20).until(
    		    EC.presence_of_element_located((By.ID, "ctl00_PlaceHolderMain_generalSearchForm_txtGSPermitNumber"))
    	    )
            element.clear()
            element.send_keys(record_number)
            #driver.find_element_by_id('ctl00_PlaceHolderMain_generalSearchForm_txtGSParcelNo').send_keys('LLRR17-000556')
            driver.find_element_by_id("ctl00_PlaceHolderMain_btnNewSearch").click()
        except:
            driver.execute_script('document.body.style.background = "white"')
            driver.save_screenshot('ERROR-searching.png')
        try:
    	    element = WebDriverWait(driver, 20).until(
    		    EC.presence_of_element_located((By.ID, "ctl00_PlaceHolderMain_lblPermitNumber"))
    	    )
        except:
            driver.execute_script('document.body.style.background = "white"')
            driver.save_screenshot('ERROR-results.png')
        finally:
            #url = driver.getCurrentUrl()
            html = driver.page_source
    return html


def extract_record_from_html(html):
    record = {}
    record['properties'] = {}

    tree = lxml.html.fromstring(html)
    try:
        record_number = tree.get_element_by_id('ctl00_PlaceHolderMain_lblPermitNumber')
        record['record_number'] = record_number.text_content()

        record_status = tree.get_element_by_id('ctl00_PlaceHolderMain_lblRecordStatus')
        record['record_status'] = record_status.text_content()

        record_expiration = tree.get_element_by_id('ctl00_PlaceHolderMain_lblExpirtionDate')
        record['record_expiration'] = record_expiration.text_content()

        #landlord = tree.cssselect('#ACA_ConfigInfo ACA_FLeft')
        landlord = " ".join(tree.xpath('//*[@id="ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList"]/tbody/tr/td[1]/div/div[1]/ul/table[1]')[0].text_content().split())
        record['landlord'] = landlord

        landlord_contact = tree.xpath('//*[@id="ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList"]/tbody/tr/td[1]/div/div[1]/ul/table[2]')[0].text_content()
        record['landlord_contact'] = landlord_contact

        record['manager'] = ''
        record['manager_contact'] = ''
        try:
            manager = " ".join(tree.xpath('//*[@id="ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList"]/tbody/tr/td[2]/div/div[1]/ul/table[1]')[0].text_content().split())
            record['manager'] = manager
            manager_contact = tree.xpath('//*[@id="ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList"]/tbody/tr/td[2]/div/div[1]/ul/table[2]')[0].text_content()
            record['manager_contact'] = manager_contact
        except: # not all records have a manager
            pass
        for i in range(2,1000): # each record can have multiple properties. We iterate over the first 998. Start counting at 2
            try:
                parcel_number = tree.xpath('//*[@id="trASITList"]/td/table/tbody/tr[{0}]/td/div/div[4]/span'.format(i,))[0]
                record['properties'][i-1] = {}
                record['properties'][i-1]['parcel_number'] = parcel_number.text_content()
                number_of_units = tree.xpath('//*[@id="trASITList"]/td/table/tbody/tr[{0}]/td/div/div[8]/span'.format(i))[0]
                record['properties'][i-1]['number_of_units'] = number_of_units.text_content()
            except IndexError as e:
                break
    except:
        print "Error skipped"
        pass
    return record


def fetch_latest_list():
    url = 'http://www.indy.gov/eGov/City/DCE/Licenses/Pages/Home.aspx'
    try:
        f = urllib2.urlopen(url)# opener.open(url)
    except urllib2.URLError as e:
        print 'Error fetching home page {0}'.format(e,)

    html = f.read()
    tree = lxml.html.fromstring(html)
    file_link = tree.cssselect('#ctl00_cphMainContent_ctl01__ControlWrapper_RichHtmlField > div:nth-child(4) > a:nth-child(1)')

    file_name = file_link[0].attrib['href'].split('/')[-1]

    url_prefix = 'http://www.indy.gov/'
    file_url = url_prefix + file_link[0].attrib['href']

    print file_name
    print file_url

    if not os.path.isfile(file_name):
        try:
            f = urllib2.urlopen(file_url)
        except urllib2.URLError as e:
            print 'Error fetching registry file {0}'.format(e,)
        finally:
            with open(os.path.basename(file_name), "wb") as local_file:
                local_file.write(f.read())

    reg_book = xlrd.open_workbook(filename=file_name)
    reg_sheet = reg_book.sheet_by_index(0)


    driver = webdriver.PhantomJS()
    # Can pick one of these for testing
    #record_number = 'LLRR17-000556' # single property, landlord and manager
    #record_number = 'LLRR17-000574' #multiple properties registered, only landlord

    # iterate through spreadsheet starting at the second row
    for row_idx in range(1, reg_sheet.nrows):

#    for row_idx in range(1, 20): # for testing just do first 5
        if reg_sheet.cell(row_idx, 0).value != reg_sheet.cell(row_idx-1, 0).value:
            record_number = reg_sheet.cell(row_idx, 0).value
            print "record:", reg_sheet.cell(row_idx, 0).value
            print "parcel:", reg_sheet.cell(row_idx, 2).value
            if registration.objects.filter(record__exact=record_number).count() == 0:
                html = get_record_html(driver, record_number)
                record = extract_record_from_html(html)
                print record
                for reg_prop in record['properties']:
                    try:
                        this_parcel = parcel.objects.get(id=record['properties'][reg_prop]['parcel_number'])
                    except parcel.DoesNotExist as e:
                        continue
                    this_record = record['record_number']
                    this_landlord = record['landlord']
                    this_landlord_contact = record['landlord_contact']
                    this_manager = record['manager']
                    this_manager_contact = record['manager_contact']
                    this_expiration = datetime.strptime(record['record_expiration'], '%m/%d/%Y')
                    this_link = ''
                    r = registration(
                        parcel=this_parcel,
                        landlord=this_landlord,
                        landlord_contact=this_landlord_contact,
                        manager=this_manager,
                        manager_contact=this_manager_contact,
                        expiration=this_expiration,
                        link=this_link,
                        record=this_record,
                        )
                    r.save()

    driver.quit()


class Command(BaseCommand):
    help = 'Update registry'

    def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        fetch_latest_list()
