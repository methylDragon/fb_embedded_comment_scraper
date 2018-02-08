# -*- coding: utf-8 -*-
"""
fb_embedded_comment_scraper()
@author: methylDragon

Description:
This script extracts JSON data that Facebook uses to power its embedded comment
platform, picking out comments. (TO A MAXIMUM OF 100 COMMENTS PER LINK!)

It can display nested replies, all in order too!

It writes to a specified .csv file the parsed data with columns:
Reply Depth | Link | Description | Total Comments | Username | City | Date-Time | Comment | Likes | Replies
"""

from datetime import datetime
import requests
import json
import csv

# =============================================================================
# SET PARAMETERS
# =============================================================================

if __name__ == "__main__":
    url = ["www.methyldragon.com"] # INSERT URLS HERE

# State the path to your desired .csv file here!
f = 'comments.csv'

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
    print("\nCompleted analysing comment #", str(len(comment_counter)) + str(" *" * reply_depth), sep="")
    print(comment)
    
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

with open(f, 'w', encoding='utf-8', newline="") as file:
    writer = csv.writer(file, delimiter=",")
    writer.writerow("Reply Depth|Link|Description|Total Comments|Username|City|Date-Time|Comment|Likes|Replies".split(sep="|"))
    
    for i,j in enumerate(url):
        # Empty variables before each iteration
        print("\nParsing Comment Section #" + str(i + 1), end='')
        
        page = None
        raw_source = None
        comments = []
        parsed_json = None
        
        # Download the page
        page = requests.get('https://www.facebook.com/plugins/feedback.php?api_key&href=' + url[i] + '&numposts=100')
        
        # Extract the HTML source code
        raw_source = page.text
        
        # Isolate the JSON section (57 added because it is the length of the suffix)
        json_prefix = raw_source.find('[{"constructor":{"__m":"CommentsPlugin.react"},"props":')
        json_suffix = raw_source.find('{"__m":"__elem_fc9f538f_0_0"},"acrossTransitions":false}]') + 57
        
        # Store the JSON section, and parse it
        json_data = raw_source[json_prefix:json_suffix]
        parsed_json = json.loads(json_data)
        
        # =============================================================================
        # OUTPUT RELEVANT OUTPUTS
        # =============================================================================
        
        # Check if parsed data is empty
        if parsed_json != None:
            # Extract comment and page IDs
            comment_ids = parsed_json[0]["props"]["comments"]["commentIDs"]
            page_id = parsed_json[0]["props"]["meta"]["targetFBID"]
            
            # Print comment URL and details
            print("\n------------------")
            print(parsed_json[0]["props"]["meta"]["href"])
            print("\nDescription: ",end="")
            
            try:
                print(parsed_json[0]["props"]["comments"]["idMap"][str(page_id)]["name"])
            except:
                print("<ERROR> no_description")
            
            print("------------------")
            print("Total Comments: ",end="")
            print(parsed_json[0]["props"]["meta"]["totalCount"])
            print("------------------")
            
            # List individual comments
            comments = []
            comment_count = []
            reply_tracker = []
            
            # Analyse comments and populate the comment list with the results
            for i, j in enumerate(comment_ids):
                reply_depth = 0
                append_comment(comments, j, reply_depth, comment_count)
                
            print("\nComment analysis complete!")
            print("Initialising comment writing\n")
                
            # Write comment data to .csv
            for i, j in enumerate(comments):
                # Append a line to the .csv per comment
                line = (str(j["reply_depth"]) + "|" + str(parsed_json[0]["props"]["meta"]["href"]) + "|" 
                        + str(parsed_json[0]["props"]["comments"]["idMap"][str(page_id)]["name"]) + "|" 
                        + str(i + 1) + " of " + str(parsed_json[0]["props"]["meta"]["totalCount"] + len(reply_tracker)) 
                        + "|" + str(j["username"]) + "|" + str(j["city"]) + "|" + str(j["date_time"]) + "|" 
                        + str(j["comment_text"]) + "|" + str(j["likes"]) + "|" + str(j["replies"]))
                writer.writerow(line.split(sep="|"))
                # Report back
                print("Completed writing comment #" + str(i + 1))
        else:
            # Report error if article data is empty
            print("ERROR: Could not parse article!")
            writer.writerow("Error: " + str(parsed_json[0]["props"]["meta"]["href"]) + " could not be parsed!")