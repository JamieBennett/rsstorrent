#!/usr/bin/python
#
# Script to download .torrent files from a collection of rss feeds.
#   Copyright (C) 2009 Jamie Bennett
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   10-03-2009 First Version jamie@linuxuk.org

# List of url feeds to be parsed. This entry is just an _example_. Please
# do not download illegal torrents or torrents that you do not have permisson
# to own.
FEEDS = [
	   "http://somefeedurl.com",
	]
DOWNLOAD_DIR = "/home/jamie/downloads/torrents/"
TIMESTAMP    = "/home/jamie/downloads/rsstorrent.stamp"
WGET_OPTIONS = "--content-disposition"
VERBOSE      = True

import feedparser
import pickle
import os
import urllib2
from datetime import datetime 

items = []
feed_bad = False
current_file = " "

def download(url):
    """Copy the contents of a file from a given URL
    to a local file.
    """
    remote_file = urllib2.urlopen(url)
    
    # See if this is a redirect to the real file. If so fall back to wget
    try:
        disposition = remote_file.info()['Content-Disposition']
        os.system('wget "%s" "%s" -P "%s"' % (url, WGET_OPTIONS, DOWNLOAD_DIR))
    except KeyError:
        local_file = open('%s%s' % (DOWNLOAD_DIR, url.split('/')[-1]), 'w')
        local_file.write(remote_file.read())
        local_file.close()

    remote_file.close()

# Build up a list of torrents to check
for feed_url in FEEDS: 
    feed = feedparser.parse(feed_url)

    # Valid feed ?
    if feed["bozo"] != 1:
        for item in feed["items"]:
            items.append((item["date_parsed"], item))
    else:
        if VERBOSE:    
            print "bad feed: " + feed_url
            
        feed_bad = True

timestamp_file = " "

# Just default to now in case there is no stamp file
last_check_date = datetime.today()

# Check to read the stamp file to see when we last checked for new torrents
try:
    timestamp_file = open(TIMESTAMP, 'r')
except IOError:
    if VERBOSE:
        print "Cannot open stamp file %s" % TIMESTAMP

if timestamp_file != " ":
    try:
        last_check_date = pickle.load(timestamp_file)
    except EOFError:
        if VERBOSE:
            print "Stamp file %s is empty" % TIMESTAMP

# Sort by date
items.sort();

downloaded_torrent = False

for item in items:
   # check for new items
    id = item[0]
    item_date = datetime(id[0], id[1], id[2], id[3], id[4])

    if item_date > last_check_date:
        if VERBOSE:
            print "downloading: " + item[1]["link"] 
            print "    and saving to: %s" % DOWNLOAD_DIR
   
        download(item[1]["link"].encode('unicode_escape'))
        downloaded_torrent = True

if downloaded_torrent == False:
    if VERBOSE:
        print "No new torrents to download"

if not feed_bad and len(items) > 0:
   # stamp the timestamp file
    try:
        timestamp_file = open(TIMESTAMP, 'w')
        last_item = items[len(items)-1][0]
        last_item_date = datetime(last_item[0], last_item[1], last_item[2], last_item[3], last_item[4])
        pickle.dump(last_item_date, timestamp_file)

    except IOError:
        if VERBOSE:
            print "Cannot stamp file %s" % TIMESTAMP

