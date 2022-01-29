#!/usr/bin/env python
# coding: utf-8
import praw
import getpass
import os
import hashlib
import time
import re
import sys
import smtplib
from datetime import datetime

update_interval = 60 # in seconds

#-----------------------------------------------------------------------------
# Purpose: Setup a SMTP server so the script can email the link to you
#
# @param The post, as a wrapper object (allows for information to be easily pulled
# @param The model of watch (string), for alert title (no wierd regex to pull model name from title)
#-----------------------------------------------------------------------------
def notify_me(post, watch):
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.login("[YOUR_DETAILS]", "[YOUR_DETAILS]")  # I would recomend making a new dedicated email account for this, also would use the google API login tool
    sender_email = "[YOUR_DETAILS]"
    receiver_email = "[YOUR_DETAILS]"
    subject = "Alert:  "
    subject += watch
    listing_name = post.title
    body = "reddit.com"
    body += post.permalink
    message = 'Subject: {0}\n\nTitle: {1}\nLink: {2}'.format(subject, listing_name, body)

    server_ssl.sendmail(sender_email, receiver_email, message)
    server_ssl.quit()
    try:
        file_name = "logs.txt"
        f = open(file_name, "a+")
        now = datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")
        tup = (dt, " - Emailed about: ", post.title, '\n')
        f.write("".join(tup))
    finally:
        f.close()
    time.sleep(5)


#-----------------------------------------------------------------------------
# Purpose: Connect to the reddit api server and use that connection for the wrapper so it can be easily
#           interacted with
#
# Also logs data for debugging
#-----------------------------------------------------------------------------
def create_reddit_instance():
    for i in range(3):
        entry = getpass.getpass()
        in_bytes = entry.encode()
        hashed = hashlib.sha256(in_bytes) # make sure to hash your password with the algorithm used here
        if hashed.hexdigest() == "[YOUR_DETAILS]":  # hash your email password and insert here
            print("\nWelcome George\n")
            reddit = praw.Reddit(client_id = "[YOUR_DETAILS]",  # enter the details of your API request from reddit
                                 client_secret = "[YOUR_DETAILS]",
                                 user_agent = "[YOUR_DETAILS]",
                                 username = "[YOUR_DETAILS]",
                                 password = entry,)
            entry = "kj34n53k3nk3$!jl2j35'32k5;l23j$)"  # so no password is held in memory afterwards (theres prob a better way to do this)
            in_bytes = b'kj3423jh423kj48jk2323jhbkfs2'
            try:
                file_name = "logs.txt"
                f = open(file_name, "a+")
                now = datetime.now()
                dt = now.strftime("%d/%m/%Y %H:%M:%S")
                tup = (dt, " - Successfully logged in\n")
                f.write("".join(tup))
            finally:
                f.close()
            return reddit
        else:
            entry = "kj34n53k3nk3$!jl2j35'32k5;l23j$)"  # again, so no password is held in memory afterwards
            in_bytes = b'kj3423jh423kj48jk2323jhbkfs2'
            print("Bad password")
    try:
        file_name = "logs.txt"
        f = open(file_name, "a+")
        now = datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")
        tup = (dt, " - 3 failed login attempts, closed script\n")
        f.write("".join(tup))
    finally:
        f.close()
    print("3 Incorrect attempts, closing...")
    sys.exit()

#-----------------------------------------------------------------------------
# Purpose: Imports models you are looking for from a txt file (allows for quick changing of models to look
#           for without having to modify the code every time
#
# @return array of models in string form
#-----------------------------------------------------------------------------
def import_models():
    model_list = []
    print("Reading models from 'models.txt'...\n")
    try:
        with open("models.txt", "r", newline=os.linesep) as file:
            for line in file:
                model_build = ""
                for c in line:
                    if c == ';':
                        print(model_build)
                        model_list.append(model_build)
                        break
                    model_build += c
    except:
        print("Please create a file named 'models.txt' and add model names/numbers(keywords)")
        print("exiting")
        sys.exit()
    finally:
        file.close()
    return model_list

#-----------------------------------------------------------------------------
# Purpose: Is in charge of setting up and running like a server program (constantly running)
#-----------------------------------------------------------------------------
def main():
    print("please enter password for user: [YOUR_DETAILS]")
    reddit = create_reddit_instance()
    MODELS_LIST = import_models()
    script_running = 1
    r_watchexchange = reddit.subreddit("watchexchange")
    print()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("Starting time: " + current_time)
    print("Monitoring...")
    latest_title = "skip first search"
    while script_running == 1:
        new = r_watchexchange.new(limit=50)
        for post in new:
            if (post.title == latest_title):
                break
            if re.search("WTS", post.title, re.IGNORECASE):
                for model in MODELS_LIST:
                    if re.search(model, post.title, re.IGNORECASE):
                        notify_me(post=post, watch=model)
        new = r_watchexchange.new(limit=1)
        latest = next(new)
        latest_title = latest.title
        time.sleep(update_interval)

#-----------------------------------------------------------------------------
# Purpose: Good general practice in python
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
