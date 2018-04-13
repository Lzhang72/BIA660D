# This is the scraper for amazon review, the feature I scrap are review rating, review title, reviewer name, review date,review content, validated purchase only, 2017 and 2018.
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import random
import time
from selenium.webdriver.common.keys import Keys
import pandas as pd
import requests
import bs4
import matplotlib.pyplot as plt
driver = webdriver.Firefox(executable_path='geckodriver.exe')
driver.get('https://www.amazon.com/RockBirds-Flashlights-Bright-Aluminum-Flashlight/product-reviews/B00X61AJYM')
normal_delay = random.normalvariate(5, 0.5)
time.sleep(normal_delay)
verify_button = driver.find_element_by_css_selector('#a-autoid-5-announce')
verify_button.click()
normal_delay = random.normalvariate(1, 0.2)
time.sleep(normal_delay)
verify_select = driver.find_element_by_css_selector('#reviewer-type-dropdown_1')
verify_select.click()
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
sort_type = driver.find_element_by_css_selector('#a-autoid-4-announce')
sort_type.click()
normal_delay = random.normalvariate(1, 0.2)
time.sleep(normal_delay)
sort_select = driver.find_element_by_css_selector('#sort-order-dropdown_1')
sort_select.click()
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
review_record = []
year = 2018
while year != 2016:
    review_block = driver.find_element_by_id('cm_cr-review_list')
    review_section = review_block.find_elements_by_class_name('review')
    url = driver.current_url
    soup = bs4.BeautifulSoup(requests.get(url).text, 'html5lib')
    time.sleep(normal_delay)
    revbox = soup.find_all('div', attrs={'class': 'a-section review'})
    while len(revbox) == 0:
        soup = bs4.BeautifulSoup(requests.get(url).text, 'html5lib')
        revbox = soup.find_all('div', attrs={'class': 'a-section review'})
    rate_box = []
    for b in revbox:
        a = b.find('span', attrs={'class': 'a-icon-alt'})
        rate_box.append(float(a.text.replace(" out of 5 stars", "")))
    for r in review_section:
        rating = rate_box[review_section.index(r)]
        title = r.find_element_by_class_name('review-title').text
        author = r.find_element_by_class_name('author').text
        date = r.find_element_by_class_name('review-date').text
        review_text = r.find_element_by_class_name('review-text').text
        if date.endswith('2016'):
            year = 2016
            break
        else:
            row_record = [rating,title,author,date,review_text]
            review_record.append(row_record)
    nextbutton = driver.find_element_by_class_name('a-last').find_element_by_tag_name('a')
    nextbutton.click()
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
head = ['rating','title','author','date','review_text']
DF = pd.DataFrame.from_records(review_record,columns = head)
DF.to_json('reviews.json')
