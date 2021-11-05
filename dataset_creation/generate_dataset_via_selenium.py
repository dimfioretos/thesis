#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleaning steps:
1. Insert newline before tweet separator:
    sed -i $'s!----------!\\\n----------!g' *
2. Remove lines with only numbers:
    sed -i '/^[[:digit:]]*$/d'
3. Move each tweet to one line:
    import os
    for file_name in os.listdir():
        data = open(file_name).read()
        with open('final.txt', 'a') as outfile:
            for item in data.split('----------'):
                tweet = " ".join(item.split('\n')[4:])
                outfile.write("%s\n" % (tweet))
4. Use the cleaning steps of generate_dataset.py (except the newline one)
"""

import os
import time

from selenium import webdriver


FAKE_NEWS_SITES = [
    "aetos-apokalypsis.com",
    "amazonios.net",
    "anastoxasmoi.gr",
    "anixneuseis.gr",
    "athensmagazine.gr",
    "attikanea.info",
    "defencenet.gr",
    "dimpenews.com",
    "emperorsclothes.gr",
    "greeknewsondemand.com",
    "hellas-now.com",
    "katohika.gr",
    "mainlynews.gr",
    "makeleio.gr",
    "oparlapipas.gr",
    "press-gr.com",
    "pronews.gr",
    "taxidromos.gr",
    "triklopodia.gr",
    "voicenews.gr"
]

NON_FAKE_NEWS_SITES = [
    "alfavita.gr",
    "amna.gr",
    "capital.gr",
    "cnn.gr",
    "dikaiologitika.gr",
    "documentonews.gr",
    "enikos.gr",
    "ert.gr",
    "huffingtonpost.gr",
    "in.gr",
    "koutipandoras.gr",
    "lifo.gr",
    "naftemporiki.gr",
    "news247.gr",
    "protothema.gr",
    "skai.gr",
    "tanea.gr",
    "thepressproject.gr",
    "thetoc.gr",
    "tovima.gr"
]

SEARCH_WORDS = [
    "covid",
    "κορονοϊός",
    "κοροδοϊός",
    "εμβόλιο",
    "εμβολιασμός",
    "αντιεμβολιαστές",
    "κρούσματα",
    "μπόλι",
    "lockdown"
]

SLEEP_TIME = 15

def main():
    """main function"""
    driver = webdriver.Firefox()
    driver.get("https://twitter.com/i/flow/login")
    time.sleep(SLEEP_TIME)
    elem = driver.find_element_by_name("username")
    elem.send_keys(os.getenv("TWITTER_USERNAME"))
    elem = driver.find_elements_by_xpath("//*[contains(text(), 'Next')]")
    elem[0].click()
    time.sleep(SLEEP_TIME)
    elem = driver.find_element_by_name("password")
    elem.send_keys(os.getenv("TWITTER_PASSWORD"))
    elem = driver.find_elements_by_xpath("//*[contains(text(), 'Log in')]")
    elem[0].click()
    time.sleep(SLEEP_TIME)

    for site in FAKE_NEWS_SITES:
        for search_term in SEARCH_WORDS:
            query = "%s %s" % (site, search_term)

            driver.get("https://twitter.com/search-advanced")
            time.sleep(SLEEP_TIME)
            elem = driver.find_element_by_name("allOfTheseWords")
            elem.send_keys(query)
            elem = driver.find_elements_by_xpath("//*[contains(text(), 'Search')]")
            elem[0].click()
            time.sleep(SLEEP_TIME)
            for _ in range(15):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            articles = driver.find_elements_by_css_selector('article')
            tweets = [x.text for x in articles]

            with open("dataset_selenium/fake/" + "_".join(query.split()) + '.txt', 'w') as outfile:
                for tweet in tweets:
                    outfile.write(tweet)
                    outfile.write("----------\n")

    for site in NON_FAKE_NEWS_SITES:
        for search_term in SEARCH_WORDS:
            query = "%s %s" % (site, search_term)

            driver.get("https://twitter.com/search-advanced")
            time.sleep(SLEEP_TIME)
            elem = driver.find_element_by_name("allOfTheseWords")
            elem.send_keys(query)
            elem = driver.find_elements_by_xpath("//*[contains(text(), 'Search')]")
            elem[0].click()
            time.sleep(SLEEP_TIME)
            for _ in range(15):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            articles = driver.find_elements_by_css_selector('article')
            tweets = [x.text for x in articles]

            with open("dataset_selenium/non_fake/" + "_".join(query.split()) + '.txt', 'w') as outfile:
                for tweet in tweets:
                    outfile.write(tweet)
                    outfile.write("----------\n")
###############################################################################


if __name__ == '__main__':
    main()
