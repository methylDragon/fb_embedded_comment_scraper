# -*- coding: utf-8 -*-
"""
fb_embedded_comment_scraper()
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
This script extracts JSON data that Facebook uses to power its embedded comment
platform, picking out comments. (TO A MAXIMUM OF 100 COMMENTS PER LINK!)

It can display nested replies, all in order too!

It writes to a specified .csv file the parsed data with columns:
Reply Depth |@@@| Link |@@@| Description |@@@| Total Comments |@@@| Username |@@@| City |@@@| Date-Time |@@@| Comment |@@@| Likes |@@@| Replies
"""

from datetime import datetime
import requests
import json
import csv
from domain_link_scraper import get_domain_links

import sys
import logging
import socket
import time
from timeit import default_timer as timer

# =============================================================================
# SET PARAMETERS HERE!
# =============================================================================

if __name__ == "__main__":

    """
    NOTE: Make sure there's no http:// or https:// in the source_URL list

    If you want to crawl something like
    "troublesome_site.com/page=<??>/other_stuff"

    Write it as a tuple! ("troublesome_site.com/page=","/other_stuff)
    """

    # [[INSERT YOUR DOMAINS HERE!]]
    # SG, ASIAPACIFIC, HEALTH, COMMENTARY,
    source_URLs = [# [CNA] SG
                   #("www.channelnewsasia.com/archives/8396078/news?pageNum=","&channelId=7469254"),
                   
                   # [CNA] ASIA PACIFIC
                   ("www.channelnewsasia.com/archives/8395764/news?pageNum=","&channelId=7469252"),
                   
                   # [CNA] HEALTH
                   ("www.channelnewsasia.com/archives/8395790/news?pageNum=","&channelId=7469578"),
                   
                   # [CNA] COMMENTARY
                   ("www.channelnewsasia.com/archives/8550254/news?pageNum=","&channelId=8396306")]

    # If you want to pull all pages from a site, ensure the site's page
    # structure is numeric (Eg. somesite.com/page/<NUMBER> )

    start_page = 0
    end_page = 99999

# =============================================================================
# SETTING ENVIRONMENT VARIABLES
# =============================================================================

# Timer!
start = timer()

# Set time format depending on your system architecture
# This works for me, but it might not work for you! Make sure to check!
if sys.platform[0:3] == "win":
    time_format = "%d %B %Y %H:%M"
else:
    time_format = "%b %d, %Y %I:%M%p"

# Agent header for reducing 403 errors (makes you look like a user)
user_agent_header = {'headers':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}

# Global comment total
overall_comment_counter = 0

# User agent header setting
user_agent_header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

# Let's turn off annoying messages, shall we?
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("bs4").setLevel(logging.ERROR)

# =============================================================================
# Useful Functions
# =============================================================================

# Check for internet
def internet(host="8.8.8.8", port=53, timeout=3):
    """
       Host: 8.8.8.8 (google-public-dns-a.google.com)
       OpenPort: 53/tcp
       Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print(ex)
        return False

# Check JSON title output
def description(output, url):
    if output is "":
        p = requests.get(url, headers = user_agent_header)
        pt = p.text
        return pt[pt.find('<title>') + 7 : pt.find('</title>')]
    else:
        return output


#SWAG
methylDragon = '''

                       .     .
                    .  |\-^-/|  .
                   /| } O.=.O { |\\
                  /´ \ \_ ~ _/ / `\\
                /´ |  \-/ ~ \-/  | `\\
                |   |  /\\\ //\\  |   |
                 \|\|\/-""-""-\/|/|/
                         ______/ /
                         '------'
           _   _        _  ___
 _ __  ___| |_| |_ _  _| ||   \ _ _ __ _ __ _ ___ _ _
| '  \/ -_)  _| ' \ || | || |) | '_/ _` / _` / _ \ ' \\
|_|_|_\___|\__|_||_\_, |_||___/|_| \__,_\__, \___/_||_|
                   |__/                 |___/
-------------------------------------------------------
                github.com/methylDragon\n'''

print(methylDragon)
print("Facebook Embedded Comment Scraper by methylDragon!")
for i in range(5):
    print("." * (5 - i))
    time.sleep(1)

print("\nINITIALISED!\n")

time.sleep(1)

# =============================================================================
# CORE CODE
# =============================================================================

# This function fetches comments from the nested dictionary from the JSON from each URL!
def fetch_comment(comment_id, reply_depth):
    user_id = parsed_json[0]["props"]["comments"]["idMap"][str(comment_id)]["authorID"]

    # Default 0, unless the comment is a child of a parent comment
    reply_depth = reply_depth

    try:
        username = parsed_json[0]["props"]["comments"]["idMap"][str(user_id)]["name"]
    except:
        username = "<ERROR> no_name"

    try:
        city = parsed_json[0]["props"]["comments"]["idMap"][str(user_id)]["bio"]["stats"]["city"]["name"]
    except:
        city = "<ERROR> no_city"

    comment_text = parsed_json[0]["props"]["comments"]["idMap"][str(comment_id)]["body"]["text"]
    timestamp = parsed_json[0]["props"]["comments"]["idMap"][str(comment_id)]["timestamp"]["text"]

    # NOTE: You might have to change the time format depending on your system
    parsed_timestamp = datetime.strptime(timestamp, time_format)
    likes = parsed_json[0]["props"]["comments"]["idMap"][str(comment_id)]["likeCount"]

    try:
        replies = parsed_json[0]["props"]["comments"]["idMap"][str(comment_id)]["public_replies"]["totalCount"]
    except:
        replies = 0

    # We return the username, timestamp, and comment text
    return {"reply_depth": reply_depth * "*", "username": username, "city": city, "date_time": parsed_timestamp, "comment_text": comment_text, "likes": likes, "replies": replies}

# This function appends comments to a comment list, and recursively appends comment replies and their replies to the same list, all in order!
def append_comment(comment_list, comment_id, reply_depth, comment_counter):

    # Fetch comment data
    comment = fetch_comment(comment_id, reply_depth)
    comment_list.append(comment)

    # Print user feedback and increase comment counter
    comment_counter.append("*" * reply_depth)
    #print("\nCompleted analysing comment #", str(len(comment_counter)) + str(" *" * reply_depth), sep="")
    #print(comment)

    # Track replies for counting total
    if reply_depth > 0:
        reply_tracker.append("*")

    # Check for replies
    try:
        reply_ids = parsed_json[0]["props"]["comments"]["idMap"][str(comment_id)]["public_replies"]["commentIDs"]

        # Increment reply_depth
        reply_depth += 1

        # Report back if found
        print("\nReplies found! New Depth:", reply_depth)

        # Append replies in order to main comment list
        for reply in reply_ids:
            # Recursively do it for replies to replies to replies ad nauseum
            append_comment(comment_list, reply, reply_depth, comment_counter)
    except:
        if reply_depth > 0:
            print("\nEnd of reply thread! Reply Depth returning to:", reply_depth - 1)

    return

# =============================================================================
# START LOOP
# =============================================================================

# MEMOISATION~~~~
parsed_urls = []
skips = 0

# This is for pages that don't throw a 404 after you exceed their content
# pages. The domain_link_scraper will still return values, but they'll already
# be parsed.
skip_loop_flag = False
skip_loop_counter = 0

# This is for breaking out of a domain if too many pages were parsed with
# no new comments found. (It's the second layer of safeguarding against
# being stuck in a domain forever)
no_comment_flag = False
no_comment_counter = 0

# =============================================================================
# LOOP THROUGH EACH STATED DOMAIN URL
# =============================================================================

# For each source (domain) stated
for source in source_URLs:

    # Initialise counter values
    section_counter = 0 # Unique sections
    populated_section_counter = 0 # Useful sections
    page_counter = 0 # Pages parsed
    comment_counter = 0 # Comments pulled from source
    no_comment_counter = 0 # Source Escape counter reset

    # Strip http:// and https://
    if source[:7] == "http://":
        source = source[7:]
    elif source[:8] == "https://":
        source = source[8:]

    # Clean source name (removing invalid characters for the saved file)
    if type(source) == str:
        cleaned_source = str(source)
    else:
        cleaned_source = str(source[0])

    # Invalid characters for file names here:
    rep_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    for char in rep_chars:
        cleaned_source = cleaned_source.replace(char,"_")

    # Prepare .csv for each source
    f = cleaned_source + '.csv'

    # Open .csv for the current source
    with open(f, 'w', encoding='utf-8', newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow("Reply Depth|@@@|Link|@@@|Description|@@@|Total Comments|@@@|Username|@@@|City|@@@|Date-Time|@@@|Comment|@@@|Likes|@@@|Replies".split(sep="|@@@|"))

        # =============================================================================
        # LOOP THROUGH EACH LIST OF URLs IN EACH PAGE OF THE DOMAIN
        # =============================================================================

        # Generate url_lists for every page in source
        # get_domain_links is a generator function!
        for url_list, current_page in get_domain_links(source, start_page, end_page):

            # If the URL list is empty, just go to the next page
            if url_list is None:
                continue

            urls = url_list
            page_counter += 1

            # Count the number of consecutive times no new articles were found in an entire
            # page's url list
            if skip_loop_flag == True:
                skip_loop_counter += 1
                print("{! WARNING !} No New Pages! Streak:", skip_loop_counter)
            else:
                skip_loop_counter = 0

            # Count the number of times no new comments were found in an entire page's url list
            if no_comment_flag == True:
                no_comment_counter += 1
            else:
                no_comment_counter = 0

            # If it crosses 5 consecutive times, stop searching the domain and move on
            if skip_loop_counter >= 5:
                print("\n\nSTOPPING SEARCH AFTER TOO MANY TIMES OF NO NEW ARTICLES CONSECUTIVELY FOUND")
                print("\nMoving on to next domain...")

                skip_loop_counter = 0

                break

            # If it crosses 500 consecutive times, stop searching the domain and move on
            if no_comment_counter >= 500:
                print("\n\nSTOPPING SEARCH AFTER TOO MANY TIMES OF NO NEW COMMENTS CONSECUTIVELY FOUND")
                print("\nMoving on to next domain...\n\n")

                no_comment_counter = 0

                break

            skip_loop_flag = True
            no_comment_flag = True

            # =============================================================================
            # LOOP THROUGH EACH LINK IN THE LIST OF URLs
            # =============================================================================

            # And run through every Facebook comment widget in every link in each page
            for url in urls:

                # If we've parsed a comment section before, skip it
                if url in parsed_urls:
                    print("Skipping parsed comment section", url)
                    continue
                else:
                    # Otherwise, add to memoisation list
                    skip_loop_flag = False # New article found in page!
                    parsed_urls.append(str(url))
                    section_counter += 1

                # Internet connectivity check
                # INFINITE LOOP IF THERE'S NO INTERNET
                while not internet():
                    print("NO INTERNET. RECONNECTING...")
                    # Wait 5s to check again
                    time.sleep(5)

                # Timing checkpoint!
                checkpoint = timer()

                # Print running summary
                print("\n\nRunning Summary for: " + str(cleaned_source))
                print("------------------")
                print("Unique Comment Sections: " + str(section_counter)
                + " | Useful Sections: " + str(populated_section_counter)
                + " | Pages Parsed: " + str(page_counter)
                + "\n------------------"
                + "\nTime Elapsed: " + str(round(checkpoint - start, 2))
                + " | Current Page: #" + str(current_page)
                + " | Total Comments: " + str(comment_counter))
                print("------------------\n")

                if skip_loop_flag == True:
                    print("{! WARNING !} No New Pages! Streak:", skip_loop_counter)
                if no_comment_counter > 1 == True:
                    print("{! WARNING !} No New Comments! Streak:", no_comment_counter)

                # Empty variables before each iteration
                page = None
                raw_source = None
                comments = []
                parsed_json = None

                # Download the page
                page = requests.get('https://www.facebook.com/plugins/feedback.php?api_key&href=' + url + '&numposts=100', headers = user_agent_header)

                # Extract the HTML source code
                raw_source = page.text

                # Isolate the JSON section (81 added because it is the length of the suffix)
                json_prefix = raw_source.find('[{"constructor":{"__m":"CommentsPlugin.react"},"props":')

                # Future-proofing this in the short-term, just in case Facebook adds stuff to the JSON suffix
                json_suffix_start = raw_source.find('{"__m":"__elem_fc9f538f_0_0"}')
                # Find the end of the tag, wherever it is
                json_suffix = json_suffix_start + raw_source[json_suffix_start:].find(']') + 1

                # Store the JSON section, and parse it
                json_data = raw_source[json_prefix:json_suffix]

                # Attempt to parse JSON (This breaks easily)
                try:
                    parsed_json = json.loads(json_data)

                # Skip if it fails
                except:
                    print("Failed to parse JSON, Skipping")
                    skips += 1
                    continue

                # =============================================================================
                # OUTPUT AND WRITE RELEVANT OUTPUTS
                # =============================================================================

                # Check if parsed data is empty
                if parsed_json != None:

                    # Extract comment and page IDs
                    comment_ids = parsed_json[0]["props"]["comments"]["commentIDs"]
                    page_id = parsed_json[0]["props"]["meta"]["targetFBID"]

                    # Print comment URL and details
                    #print("\n------------------")
                    #print(parsed_json[0]["props"]["meta"]["href"])
                    #print("\nDescription: ",end="")

                    print("\nArticle: " + url + "\n")

                    try:
                        # Print name
                        print(parsed_json[0]["props"]["comments"]["idMap"][str(page_id)]["name"])
                        print()
                        populated_section_counter += 1
                        no_comment_flag = False # Comments were found in page!
                    except:
                        print("{ NO COMMENTS FOUND }")

                    #print("------------------")
                    #print("Total Comments: ",end="")
                    #print(parsed_json[0]["props"]["meta"]["totalCount"])
                    #print("------------------")

                    # List individual comments
                    comments = []
                    comment_count = []
                    reply_tracker = []

                    # Analyse comments and populate the comment list with the results
                    for comment_id in comment_ids:
                        reply_depth = 0
                        append_comment(comments, comment_id, reply_depth, comment_count)

                    #print("\nComment analysis complete!")
                    #print("Initialising comment writing\n")

                    # Write comment data to .csv
                    for comment_index, comment in enumerate(comments, 1):

                        # Append a line to the .csv per comment
                        line = (# Reply depth
                                str(comment["reply_depth"])
                                + "|@@@|"

                                # Link
                                + str(parsed_json[0]["props"]["meta"]["href"])
                                + "|@@@|"

                                # Description
                                + description(str(parsed_json[0]["props"]["comments"]["idMap"][str(page_id)]["name"]), url)
                                + "|@@@|"

                                # Comment number (out of total comments in post)
                                + str(comment_index)
                                + " of "
                                + str(parsed_json[0]["props"]["meta"]["totalCount"]
                                + len(reply_tracker))
                                + "|@@@|"

                                # Commenter name
                                + str(comment["username"])
                                + "|@@@|"

                                # Commenter city
                                + str(comment["city"])
                                + "|@@@|"

                                # Timestamp
                                + str(comment["date_time"])
                                + "|@@@|"

                                # Comment text
                                + str(comment["comment_text"])
                                + "|@@@|"

                                # Likes comment has
                                + str(comment["likes"])
                                + "|@@@|"

                                # Replies comment has
                                + str(comment["replies"])
                                )

                        # Increment intra-source comment total
                        comment_counter += 1

                        # Write the comment into the .csv
                        writer.writerow(line.split(sep="|@@@|"))
                        # Report back
                        print("Completed writing comment #" + str(comment_index))
                else:
                    # Report error if article data is empty
                    print("ERROR: Could not parse article!")
                    writer.writerow("Error: " + str(parsed_json[0]["props"]["meta"]["href"]) + " could not be parsed!")

    # Global comment total
    overall_comment_counter += comment_counter

# Timing checkpoint!
checkpoint = timer()

print(methylDragon[:101])

# Print concluding summary
print("\n------------------")
print("Concluding Summary:")
print("------------------\n")
print("Total Parsed URLs:", str(len(parsed_urls)))
print("Error Skips:", skips)
print("Total Time:", str(round(checkpoint - start, 2)))
print("Overall Total Scraped Comments:", str(overall_comment_counter))