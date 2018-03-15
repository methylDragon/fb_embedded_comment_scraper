# -*- coding: utf-8 -*-
"""
domain_link_scraper()
@author: methylDragon

                                   .     .
                                .  |\-^-/|  .
                               /| } O.=.O { |\
                              /´ \ \_ ~ _/ / `\
                            /´ |  \-/ ~ \-/  | `\
                            |   |  /\\ //\  |   |
                             \|\|\/-""-""-\/|/|/
                                     ______/ /
                                     '------'
                       _   _        _  ___
             _ __  ___| |_| |_ _  _| ||   \ _ _ __ _ __ _ ___ _ _
            | '  \/ -_)  _| ' \ || | || |) | '_/ _` / _` / _ \ ' \
            |_|_|_\___|\__|_||_\_, |_||___/|_| \__,_\__, \___/_||_|
                               |__/                 |___/
            -------------------------------------------------------
                           github.com/methylDragon

Description:
This script lets you (naively) run through every single page in a given
source, extracting a unique list of every internal link mentioned in <a> tags
in the page.

The list outputs both http:// and https:// versions of relative links to aid
in ambiguous comment scraping from Facebook's comment widget

Functions:
- get_domain_links(domain, start_page = 1, end_page = 99999)
(This is a generator function! Just keep calling it to get the next url list!)
(Make sure that the "domain" is something like "website.com/page/"<page # here>)
(Scrape from start page, up to but not including the end page)

- get_links(url, internal = False, custom_domain = "")
(Scrape all links from url)
(Set internal as True if you only want pages from the source URL)
(Set the custom_domain if you want the internal link checker to use another
url as the source, but still want to scrape from the url)
"""

from bs4 import BeautifulSoup
import requests
import re
import logging
import time
import random

# Agent header for reducing 403 errors (makes you look like a user)
user_agent_header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

# Turn off annoying messages
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("bs4").setLevel(logging.ERROR)

# Link scraping function
def get_links(url, internal = False, custom_domain = ""):

    # Download and parse the page
    html_page = requests.get(url, headers = user_agent_header)
    soup = BeautifulSoup(html_page.text, "lxml")

    # Initialise the URL list
    found_links = []

    # If we want internal URLs only, prepare the regex filtering term
    if internal != False:

        # If no custom_domain stated, strip all urls of prefixes
        if custom_domain == "":
            if url[:7] == "http://":
                url = url[7:]
            elif url[:8] == "https://":
                url = url[8:]

        # Otherwise, set the filtering term as the custom_domain
        else:
            if custom_domain[:7] == "http://":
                custom_domain = custom_domain[7:]
            elif custom_domain[:8] == "https://":
                custom_domain = custom_domain[8:]
            url = custom_domain

    # Else, filter out nothing
    else:
        url = ""

    # Add in absolute links, filtering out unwanted links using BeautifulSoup
    for link in soup.findAll('a', attrs={'href': re.compile("^http[s]?://" + url)}):
        found_links.append(link.get('href'))

    # Add in relative links (both HTTP and HTTPS versions)
    for link in soup.findAll('a', attrs={'href': re.compile("^/")}):
        found_links.append("https://" + url + link.get('href'))
        found_links.append("http://" + url + link.get('href'))

    # Return the list
    return list(set(found_links))

# Link scraping function across all pages in a domain
def get_domain_links(domain, start_page = 1, end_page = 99999):

    print("FETCHING DOMAIN", str(domain))

    # Strip all prefixes
    if domain[:7] == "http://":
        domain = domain[7:]
    elif domain[:8] == "https://":
        domain = domain[8:]

    # Return the domain itself! (In case you just want to grab a single article)
    if type(domain) == str:
        yield [str("http://" + str(domain))], "BASE"
    else:
        yield [str("http://" + str(domain[0]) + str(domain[1]))], "BASE"

    # Initialise counters
    error_limit = 0
    page_counter = start_page

    # Run the infinite loop until broken out of by consecutive errors
    while True:

        if type(domain) == str:
            # Create the URL
            page_url = "http://" + str(domain) + str(page_counter)
        else:
            try:
                page_url = "http://" + str(domain[0]) + str(page_counter) + str(domain[1])
            except:
                pass

        print("\nFETCHING PAGE:", page_url)

        # Check to see if it's within the search range
        if page_counter > start_page + end_page - 1:
            print("Page fetch limit reached:", page_counter - start_page)
            return

        # Download and parse the page
        try:
            page = requests.get(page_url, headers = user_agent_header)
            # Break if there are consecutive failures to fetch the page

            # If the first time, the page returns false
            # Give it 10 minutes or so, keep retrying every 30 seconds
            if page.status_code != 200:
                error_sub_limit = 0

                # While loop for n number of minutes
                while error_sub_limit < 60:
                    page = requests.get(page_url, headers = user_agent_header)

                    print("PAGE STATUS:", page.status_code)

                    # Escape the loop if it works!
                    if page.status_code == 200:
                        break
                    else:
                        print("ERROR FETCHING DOMAIN!")
                        error_sub_limit += 1
                        print("WAITING FOR 1 HOUR:", error_sub_limit)
                        time.sleep(10)
                        print(".....")
                        time.sleep(10)
                        print("....")
                        time.sleep(10)
                        print("...")
                        time.sleep(10)
                        print("..")
                        time.sleep(10)
                        print(".")
                        time.sleep(10)

            # Final try
            page = requests.get(page_url, headers = user_agent_header)
            print("FETCH STATUS:", page.status_code)


            if page.status_code != 200:
                error_limit += 1
                print("\nNetwork Errors encountered:", error_limit)
                if error_limit > 5:
                    print("URL FETCH ERROR LIMIT REACHED, BREAKING")
                    return
            else:
                print("Page #" + str(page_counter) + " fetched")

                # Note: I use yield here so we don't actually have to
                # wait to get all the links before parsing them
                # So instead we can just parse them on a page-by-page
                # basis! Generators are great!
                if type(domain) == str:
                    yield get_links(page_url, True, domain.split("/")[0]), str(page_counter)
                else:
                    try:
                        yield get_links(page_url, True, domain[0].split("/")[0]), str(page_counter)
                    except:
                        pass

        # Or random errors occur that stop the page fetch
        except:
            error_limit += 1
            print("\nUnknown Fetch Errors encountered:", error_limit)
            if error_limit > 5:
                print("\nURL FETCH ERROR LIMIT REACHED, BREAKING")
                return

        # Increment page counter
        page_counter += 1
