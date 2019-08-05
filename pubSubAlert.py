#!/usr/bin/env python3

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

load_dotenv(find_dotenv())

storeID = os.getenv('STOREID')
sub = 'chicken tender sub' if len(sys.argv) == 1 else sys.argv[1] + " sub"
counter = 5

options = Options()
options.headless = bool(int(os.getenv("HEADLESS")))

while counter != 0:
    browser = webdriver.Firefox(options=options, log_path=os.devnull)

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
msg = sub + ' ' + sale +  " on sale!"

# determine the appropriate sale date range: thurs - wed
thurs = 3
first = datetime.datetime.today()
day = first.weekday()
if day > thurs:
    first -= datetime.timedelta(days=day-thurs)
elif day < thurs:
    first -= datetime.timedelta(days=thurs+day+1)

last = first + datetime.timedelta(days=6)
msg += " : " + first.strftime('%-m/%-d') + ' - ' + last.strftime('%-m/%-d')
print(msg)

sender = os.getenv('SENDER')
passwd = os.getenv('PASSWD')
receiver = os.getenv('RECEIVER')

if sender != '' and receiver != '' and passwd != '':
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
