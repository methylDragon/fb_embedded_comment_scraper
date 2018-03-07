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
import newspaper
from domain_link_scraper import get_links, get_domain_links
import logging
import socket
import time

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("bs4").setLevel(logging.ERROR)

# =============================================================================
# SET PARAMETERS HERE!
# =============================================================================

if __name__ == "__main__":

    # [[Insert your domains]]
    source_URLs = ["somesite.com/page/", "methylDragon.com"]

    # If you want to pull all pages from a site, ensure the site's page
    # structure is numeric (Eg. somesite.com/page/<NUMBER> )

    start_page = 0

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

#SWAG
print('''

                       .     .
                    .  |\-^-/|  .    
                   /| } O.=.O { |\\ 
                  /´ \ \_ ~ _/ / `\\
                /´ |  \-/ ~ \-/  | `\\
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
                github.com/methylDragon\n''')
    
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
def fetch_comment(i, reply_depth):
    userID = parsed_json[0]["props"]["comments"]["idMap"][str(i)]["authorID"]
    
    # Default 0, unless the comment is a child of a parent comment
    reply_depth = reply_depth
    
    try:
        username = parsed_json[0]["props"]["comments"]["idMap"][str(userID)]["name"]
    except:
        username = "<ERROR> no_name"
        
    try:
        city = parsed_json[0]["props"]["comments"]["idMap"][str(userID)]["bio"]["stats"]["city"]["name"]
    except:
        city = "<ERROR> no_city"
    
    comment_text = parsed_json[0]["props"]["comments"]["idMap"][str(i)]["body"]["text"]
    timestamp = parsed_json[0]["props"]["comments"]["idMap"][str(i)]["timestamp"]["text"]

    # NOTE: You might have to change the time format depending on your system
    parsed_timestamp = datetime.strptime(timestamp, '%d %B %Y %H:%M')
    likes = parsed_json[0]["props"]["comments"]["idMap"][str(i)]["likeCount"]
    
    try:
        replies = parsed_json[0]["props"]["comments"]["idMap"][str(i)]["public_replies"]["totalCount"]
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

# =============================================================================
# LOOP THROUGH EACH STATED DOMAIN URL
# =============================================================================

# For each source (domain) stated
for source in source_URLs:

    # Initialise counter values
    section_counter = 0 # Unique sections
    populated_section_counter = 0 # Useful sections
    page_counter = 0 # Pages parsed
    
    # Strip http:// and https://
    if source[:7] == "http://":
        source = source[7:]
    elif source[:8] == "https://":
        source = source[8:]
    
    # Clean source name (removing invalid characters for the saved file)
    cleaned_source = str(source)
    
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
        for url_list in get_domain_links(source, start_page):
            urls = url_list
            page_counter += 1
            
            # Count the number of consecutive times no new articles were found in an entire
            # page's url list
            if skip_loop_flag == True:
                skip_loop_counter += 1
                print("No new articles found! Streak: " + str(skip_loop_counter))
                skip_loop_flag = False
            else:
                skip_loop_counter = 0
                        
            # If it crosses 5 consecutive times, stop searching the domain and move on
            if skip_loop_counter >= 5:
                print("\n\nSTOPPING SEARCH AFTER TOO MANY TIMES OF NO NEW ARTICLES CONSECUTIVELY FOUND")
                print("\nMoving on to next domain...\n\n")
                break

            # =============================================================================
            # LOOP THROUGH EACH LINK IN THE LIST OF URLs
            # =============================================================================
        
            # And run through every Facebook comment widget in every link in each page
            for i, j in enumerate(urls):
                
                # If we've parsed a comment section before, skip it
                if j in parsed_urls:
                    print("Skipping parsed comment section", j)
                    skip_loop_flag = True
                    continue
                else:
                    # Otherwise, add to memoisation list
                    skip_loop_flag = False
                    parsed_urls.append(str(j))
                    section_counter += 1
                
                # Internet connectivity check
                # INFINITE LOOP IF THERE'S NO INTERNET                
                while not internet():
                    print("NO INTERNET. RECONNECTING...")
                    # Wait 5s to check again
                    time.sleep(5)
                
                # Print running summary
                print("\n\nRunning Summary for: " + str(source))
                print("------------------")
                print("Unique Comment Sections: " + str(section_counter)
                + " | Useful Sections: " + str(populated_section_counter)
                + " | Pages Parsed: " + str(page_counter))
                print("------------------\n")
                
                # Empty variables before each iteration
                page = None
                raw_source = None
                comments = []
                parsed_json = None
                
                # Download the page
                page = requests.get('https://www.facebook.com/plugins/feedback.php?api_key&href=' + urls[i] + '&numposts=100')
                
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

                    print("\nArticle: " + urls[i] + "\n")
                    
                    try:
                        # Print name
                        print(parsed_json[0]["props"]["comments"]["idMap"][str(page_id)]["name"])
                        print()
                        populated_section_counter += 1
                    except:
                        print("NO COMMENTS FOUND")
                    
                    #print("------------------")
                    #print("Total Comments: ",end="")
                    #print(parsed_json[0]["props"]["meta"]["totalCount"])
                    #print("------------------")
                    
                    # List individual comments
                    comments = []
                    comment_count = []
                    reply_tracker = []
                    
                    # Analyse comments and populate the comment list with the results
                    for i, j in enumerate(comment_ids):
                        reply_depth = 0
                        append_comment(comments, j, reply_depth, comment_count)
                        
                    #print("\nComment analysis complete!")
                    #print("Initialising comment writing\n")
                        
                    # Write comment data to .csv
                    for i, j in enumerate(comments):
                        
                        # Append a line to the .csv per comment
                        line = (# Reply depth
                                str(j["reply_depth"]) 
                                + "|@@@|"
                                
                                # Link
                                + str(parsed_json[0]["props"]["meta"]["href"]) 
                                + "|@@@|" 
                                
                                # Description
                                + str(parsed_json[0]["props"]["comments"]["idMap"][str(page_id)]["name"]) 
                                + "|@@@|" 
                                
                                # Comment number (out of total comments in post)
                                + str(i + 1) 
                                + " of " 
                                + str(parsed_json[0]["props"]["meta"]["totalCount"] 
                                + len(reply_tracker)) 
                                + "|@@@|" 
                                
                                # Commenter name
                                + str(j["username"]) 
                                + "|@@@|" 
                                
                                # Commenter city
                                + str(j["city"]) 
                                + "|@@@|"                                 

                                # Timestamp
                                + str(j["date_time"])                                 
                                + "|@@@|" 
                                
                                # Comment text
                                + str(j["comment_text"]) 
                                + "|@@@|" 
                                
                                # Likes comment has
                                + str(j["likes"])                                 
                                + "|@@@|" 
                                
                                # Replies comment has
                                + str(j["replies"])
                                )
                        
                        # Write the comment into the .csv
                        writer.writerow(line.split(sep="|@@@|"))
                        # Report back
                        print("Completed writing comment #" + str(i + 1))
                else:
                    # Report error if article data is empty
                    print("ERROR: Could not parse article!")
                    writer.writerow("Error: " + str(parsed_json[0]["props"]["meta"]["href"]) + " could not be parsed!")

# Print concluding summary
print("Summary:")
print("Total Parsed URLs:", str(len(parsed_urls)))
print("Error Skips:", skips)
