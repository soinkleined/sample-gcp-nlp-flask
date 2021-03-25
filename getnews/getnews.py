#!/usr/bin/env python3

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import re

########################################
# METHODS
########################################

def page_get(url):
    # Set up the request headers that we're going to use, to simulate
    # a request by the Chrome browser. Simulating a request from a browser
    # is generally good practice when building a scraper
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
        'Referrer': 'https://google.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    return requests.get(url, headers)

def page_post(url, payload):
    #data = requests.utils.quote(str(payload))
    return requests.post(url, data = payload)

#page=get_page('https://www.db.com/media/news')
#print(page.content)

def get_links(news_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-logging')
    CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=chrome_options)
    browser.get(news_url)
    delay = 5 # seconds
    try:
        myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'news-stream-no-results')))
    except TimeoutException:
        pass
    src = browser.page_source
    page = BeautifulSoup(browser.page_source,'html.parser')
    data = page.findAll('div',attrs={'class':'news-stream-entry'})
    l=[]
    for div in data:
        for link in div.findAll('a'):
            target = link.get('href')
            if target.startswith('//'):
                target = 'https:' + target
#            if re.match('.*/news/detail/.*', target):
            l.append(target)
    l = sorted(set(l))
    #for retlink in l:
        #print(retlink)
    browser.quit()
    return l

def get_news(url):
    for link in get_links(url):
            print(link)
            page = page_get(link)
            parse_only = SoupStrainer('div',{'class': 'news-text'})
            page_src = BeautifulSoup(page.content, 'html.parser', parse_only=parse_only)
            if len(page_src) == 0:
                parse_only = SoupStrainer('body')
                page_src = BeautifulSoup(page.content, 'html.parser', parse_only=parse_only)
            text = page_src.get_text()
            text = re.sub(r"^\s+|\s+$|\n\n", "", text)
            text = text[:521] # not sure why there is a character limit in the form or where it is set
            submit_text = { 
                    'text': text
                    }
            #NLP_result = requests.post('http://gee-nlp-project.oa.r.appspot.com/upload', data = submit_text)
            NLP_result = page_post('http://gee-nlp-project.oa.r.appspot.com/upload', submit_text)
            NLP_out = BeautifulSoup(NLP_result.content, 'html.parser')
            NLP_out = NLP_out.get_text()
            print(NLP_out)

#Explicitly call language as it responds based on geo-location
get_news('https://www.db.com/media/news?language_id=1') #English
get_news('https://www.db.com/media/news?language_id=3') #German
