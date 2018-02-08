# fb_embedded_comment_scraper
A scraper for gathering data from Facebook's embedded comment widgets on any number of URLs! It bypasses the Facebook graph API (you don't need an access token) so there's little risk of throttling.

This script extracts JSON data that Facebook uses to power its embedded comment
platform, recursively picking out comments. (TO A MAXIMUM OF 100 COMMENTS PER LINK!)

It can display nested replies, all in order too, so the .csv reads naturally like the Facebook comment feed!

It writes to a specified .csv file the parsed data with columns:
Reply Depth | Link | Description | Total Comments | Username | City | Date-Time | Comment | Likes | Replies

### Usage

Just change the relevant parameters!

```python
# =============================================================================
# SET PARAMETERS
# =============================================================================

if __name__ == "__main__":
    url = ["www.methyldragon.com"] # INSERT URLS TO PARSE HERE

# State the path to your desired .csv file here!
f = 'comments.csv'
```



### How it works

I noticed that you can access the source of the iframes that Facebook dynamically generates via embedded JS in a webpage. Said source has JSON data hidden in a mess of text that can be parsed accordingly!

### Applications

I wrote this as part of a bigger project where we wanted to do natural language processing on a dataset of comments. This can help build that dataset!