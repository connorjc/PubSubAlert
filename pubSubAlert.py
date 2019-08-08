#!/usr/bin/env python3

import argparse
import datetime
import os
import re
import sys
import smtplib
import time
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="A Publix Supermarket weekly ad \
        webcrawler designed to determine whether or not chicken tender subs are\
        on sale. The results of the search will be emailed to specified recpients.")
parser.add_argument("-d", "--dryrun", help="perform a dry run by not emailing results", action="store_true")
parser.add_argument("-s", "--sub", help="search for alternate pub sub", action="store", type=str, default="chicken tender")
args = parser.parse_args()

load_dotenv(find_dotenv())

storeID = os.getenv('STOREID')
sender = os.getenv('SENDER')
passwd = os.getenv('PASSWD')
receiver = os.getenv('RECEIVER')

sub = args.sub + " sub"
counter = 5

options = Options()
options.headless = bool(int(os.getenv("HEADLESS")))

while counter != 0:
    browser = webdriver.Firefox(options=options, service_log_path=os.devnull)

    try:
        # navigate to weeklyad
        browser.get('http://weeklyad.publix.com')

        # specify store
        browser.find_element_by_class_name('selectStoreBtn').click()
        browser.find_element_by_id('pblx-txtLocation').send_keys(storeID)
        browser.find_element_by_id('pblx-btnStoreSearch').click()
        # browser.find_element_by_class_name('js-selectStore').click()
        time.sleep(3)
        browser.find_element_by_xpath('//button[@data-number="'+storeID+'"]').click()

        # Navigate add for subs on sale
        browser.find_element_by_class_name('searchInputField').send_keys(sub)
        browser.find_element_by_id('goBtnSearchPosition').click()

        # parse page
        soup = BeautifulSoup(browser.page_source, features="html.parser")
        results = bool(int(re.match(r'(\d+)', soup.select_one('span[class="nonSneakPeekHeader"]').text).group(0)))

        sale = "are" if results else "not"
    except:
        counter -= 1
        print("Error encountered:", counter, "attempts left...")
        time.sleep(10)
    else:
        break
    finally:
        #close browser
        browser.close()

# message the masses
try:
    msg = sub + ' ' + sale +  " on sale!"
except NameError:
    msg = "failure"
    receiver = sender

# determine the appropriate sale date range: wed - tue
wed = 2
first = datetime.datetime.today()
day = first.weekday()
if day > wed:
    first -= datetime.timedelta(days=day-wed)
elif day < wed:
    first -= datetime.timedelta(days=wed+day+2)

last = first + datetime.timedelta(days=6)
msg += " : " + first.strftime('%-m/%-d') + ' - ' + last.strftime('%-m/%-d')

print(msg)

if not args.dryrun and sender != '' and receiver != '' and passwd != '':
    message = EmailMessage()

    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = sys.argv[0].split('/')[-1].split('.')[0]
    message.set_content(msg)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(sender, passwd)
    server.send_message(message)
    server.quit()
