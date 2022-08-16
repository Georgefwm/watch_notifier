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

UPDATE_INTERVAL = 60  # in seconds. Maximum time between re-checking posts

BOT_EMAIL_USR = "EMAIL_ADDRESS"
BOT_EMAIL_PASS = "PASSWORD"
EMAIL_TO_ALERT = "EMAIL_ADDRESS"


def notify_me(post, watch):
    '''
    Set up an SMTP server and send email to your personal account.

    @param post: a wrapper object (allows for information to be easily pulled
    @param watch: The model of watch (string), for alert title
    '''

    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    # I would recommend making a new dedicated email account for this, also would use the Google API login tool
    server_ssl.login(BOT_EMAIL_USR, BOT_EMAIL_PASS)

    subject = "Alert:  "
    subject += watch
    listing_name = post.title
    body = "reddit.com"
    body += post.permalink
    message = 'Subject: {0}\n\nTitle: {1}\nLink: {2}'.format(subject, listing_name, body)

    server_ssl.sendmail(BOT_EMAIL_USR, EMAIL_TO_ALERT, message)
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


def create_reddit_instance():
    '''
    Connects to the reddit api, asks for password but still not secure as hard coded(was playing around with encoding).
    Logs to logs.txt as well.

    @return: The reddit api wrapper object
    '''

    print("please enter password:")
    for i in range(3):
        entry = getpass.getpass()
        in_bytes = entry.encode()
        hashed = hashlib.sha256(in_bytes)  # make sure to hash your password with the algorithm used here

        if hashed.hexdigest() == "[YOUR_DETAILS]":  # hash your email password and insert here
            print("\nSuccessful login\n")

            reddit = praw.Reddit(client_id="[YOUR_DETAILS]",  # enter the details of your API request from reddit
                                 client_secret="[YOUR_DETAILS]",
                                 user_agent="[YOUR_DETAILS]",
                                 username="[YOUR_DETAILS]",
                                 password=entry,)

            entry = "kj34n53k3nk3$!jl2j35'32k5;l23j$)lkjh324klj5h2l3kj45hl23"
            in_bytes = b'kj3423jh423kj48jk3423jh42fs2'

            # log login success
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
            entry = "kj34n53k3nk3$!jl2j35'32k5;l23j$)lkjh324klj5h2l3kj45hl23"
            in_bytes = b'kj3423jh423kj48jk3423jh42fs2'
            print("Bad password")

    # log login failure
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


def import_models():
    '''
    Imports models you are looking for from a txt file.
    Allows for quick changing of models to look for without having to modify the code every time.

    @return: List models, as strings
    '''

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

    # Couldn't find file
    except:
        print("Please create a file named 'models.txt' and add model names/numbers(keywords)")
        print("exiting")
        sys.exit()

    finally:
        file.close()
    return model_list


def main():
    reddit = create_reddit_instance()
    models_list = import_models()
    r_watchexchange = reddit.subreddit("watchexchange")
    script_running = 1

    print()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("Starting time: " + current_time)
    print("Monitoring...")

    latest_title = "skip first search"
    while script_running == 1:
        new = r_watchexchange.new(limit=50)
        for post in new:
            if post.title == latest_title:  # Don't need to inspect posts twice or double notify
                break

            if re.search("WTS", post.title, re.IGNORECASE):
                for model in models_list:
                    if re.search(model, post.title, re.IGNORECASE):
                        notify_me(post=post, watch=model)

        new = r_watchexchange.new(limit=1)
        latest = next(new)
        latest_title = latest.title
        time.sleep(UPDATE_INTERVAL)


if __name__ == '__main__':
    main()
