#!/usr/bin/env python3

import os
import re
import sys
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup

load_dotenv(find_dotenv())

storeID = os.getenv('STOREID')

sub = 'chicken tender sub' if len(sys.argv) == 1 else sys.argv[1]

options = Options()
options.headless = bool(os.getenv("HEADLESS"))
browser = webdriver.Firefox(options=options)

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
results = int(re.match(r'(\d+)', soup.select_one('span[class="nonSneakPeekHeader"]').text).group(0))
sale = "are" if results != 0 else "not"

# message the masses
print(sub, sale, "on sale!")

browser.close()
