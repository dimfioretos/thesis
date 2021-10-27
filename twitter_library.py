#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
import pprint
import datetime
import time

import requests
import twint


def search(query, date_from=None, date_until=None, min_retweets=None, min_replies=None, min_likes=None, limit=20, username=None):
    """Get a list of tweets matching a query"""
    results = list()
    cfg = twint.Config()
    cfg.Hide_output = True
    cfg.Store_object = True
    cfg.Retweets = True
    cfg.Get_replies = True
    cfg.Store_object_tweets_list = results
    cfg.Limit = limit

    cfg.Search = query
    if date_from:
        cfg.Since = date_from
    if date_until:
        cfg.Until = date_until
    if min_retweets:
        cfg.Min_retweets = min_retweets
    if min_replies:
        cfg.Min_replies = min_replies
    if min_likes:
        cfg.Min_likes = min_likes
    if username:
        cfg.Username = username

    logging.info("Running search: %s", pprint.pformat({k:v for k, v in vars(cfg).items() if v}))
    start = time.time()

    twint.run.Search(cfg)

    logging.info("Search ended after %.2lf seconds, fetched %s results.",
                 time.time() - start, len(results))
    return results
###############################################################################


def get_replies(source_tweet, limit=1000):
    """Get a list of replies to a tweet"""
    results = list()
    cfg = twint.Config()
    cfg.Hide_output = True
    cfg.Store_object = True
    cfg.Retweets = True
    cfg.Get_replies = True
    cfg.Store_object_tweets_list = results
    cfg.Limit = limit

    cfg.To = source_tweet.username

    until = (
        datetime.datetime.strptime(source_tweet.datestamp, '%Y-%m-%d') +
        datetime.timedelta(days=2)
    ).strftime("%Y-%m-%d")

    cfg.Since = source_tweet.datestamp
    cfg.Until = until
    logging.info("Running replies search for tweet id %s : %s", source_tweet.id,
                 pprint.pformat({k:v for k, v in vars(cfg).items() if v}))
    start = time.time()

    twint.run.Search(cfg)

    tweets_found = list()
    for idx, tweet in enumerate(results):
        if tweet.conversation_id in [source_tweet.id, str(source_tweet.id)]:
            tweets_found.append(tweet)

    logging.info("Found %d reply tweets in %.2lf seconds.", len(tweets_found),
                 time.time() - start)
    return tweets_found
###############################################################################


def main():
    """main function"""
    # results = search(query = "covid19greece", min_retweets = 5, limit = 20)
    # note: the following tweet returns a single result for ease of testing during development
    results = search(query="ΕΝΝΟΕΙΤΑΙ πρέπει να ακυρωθεί η στρατιωτική παρέλαση"
                     " στη Θεσσαλονίκη λόγω του κοβιντ. Και μη μου πείτε τις "
                     " μαλακιες για διαδηλώσεις",
                    min_retweets=5, limit=20)
    print("Results found: %s" % (len(results)))
    for item in results:
        print("*"*100)
        print("Results found: %s" % (len(results)))
        pprint.pprint(vars(item))

        responses = get_replies(item)
        for response in responses:
            print("-" * 20)
            print("Response from: %s Content: %s" % (
                response.username, response.tweet))
###############################################################################


if __name__ == '__main__':
    main()
