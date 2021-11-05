#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleaning steps:
    1. Extract tweets text with jq: jq '.tweets[].text' *.json
    2. remove urls: sed -e 's!http[s]\?://\S*!!g'
    3. remove mentions: sed 's!@[^[:blank:]]*!!g'
    4. remove &amp; : sed 's!&amp;!!g'
    5. convert newlines with spaces: sed 's!\\n! !g'
    6. remove quotes: sed 's!\\"! !g'
    7. remove emoticons: python3 -c "exec(\"import sys\nimport emoji\nfor line in sys.stdin:\n sys.stdout.write(emoji.get_emoji_regexp().sub(u'', line))\")"
    8. sort and uniq tweets: sort | uniq

Note: to keep the longest of the lines with similar 50 first characters (some
tweets are partially duplicated by the same posters):
    sort input | tac | uniq -w 50 > output

All in one:
sed -e 's!http[s]\?://\S*!!g' input |\
sed 's!@[^[:blank:]]*!!g'           |\
sed 's!&amp;!!g'                    |\
sed 's!\\n! !g'                     |\
sed 's!\\"! !g'                     |\
python3 -c "exec(\"import sys\nimport emoji\nfor line in sys.stdin:\n sys.stdout.write(emoji.get_emoji_regexp().sub(u'', line))\")" |\
sort                                |\
uniq > output

"""

import json
import os

import tweepy


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

def main():
    """main function"""
    client = tweepy.Client(bearer_token=os.getenv("TWITTER_BEARER_TOKEN"))

    for site in FAKE_NEWS_SITES:
        for search_term in SEARCH_WORDS:
            query = "%s %s" % (site, search_term)
            tweets = client.search_recent_tweets(
                query=query,
                expansions = ['author_id','referenced_tweets.id','referenced_tweets.id.author_id','in_reply_to_user_id','entities.mentions.username'],
                tweet_fields=['id','text','author_id','created_at','conversation_id','entities','public_metrics','referenced_tweets'],
                user_fields=['id','name','username','created_at','description','public_metrics','verified'],
                place_fields=['full_name','id'],
                max_results=100
            )

            json_data = dict()
            if not tweets.data:
                print("No results for %s" % (query))
                json_data['tweets'] = None
                json_data['includes'] = None
            else:
                json_data['tweets'] = list(map(dict, tweets.data))
                json_data['includes'] = dict()
                for key, value in tweets.includes.items():
                    json_value = [dict(x.items()) for x in value]
                    json_data['includes'][key] = json_value
            with open("json_data/fake/" + "_".join(query.split()) + '.json', 'w') as outfile:
                json.dump(json_data, outfile, sort_keys=True, indent=4, default=str)

    for site in NON_FAKE_NEWS_SITES:
        for search_term in SEARCH_WORDS:
            query = "%s %s" % (site, search_term)
            tweets = client.search_recent_tweets(
                query=query,
                expansions = ['author_id','referenced_tweets.id','referenced_tweets.id.author_id','in_reply_to_user_id','entities.mentions.username'],
                tweet_fields=['id','text','author_id','created_at','conversation_id','entities','public_metrics','referenced_tweets'],
                user_fields=['id','name','username','created_at','description','public_metrics','verified'],
                place_fields=['full_name','id'],
                max_results=100
            )

            json_data = dict()
            if not tweets.data:
                print("No results for %s" % (query))
                json_data['tweets'] = None
                json_data['includes'] = None
            else:
                json_data['tweets'] = list(map(dict, tweets.data))
                json_data['includes'] = dict()
                for key, value in tweets.includes.items():
                    json_value = [dict(x.items()) for x in value]
                    json_data['includes'][key] = json_value
            with open("json_data/non_fake/" + "_".join(query.split()) + '.json', 'w') as outfile:
                json.dump(json_data, outfile, sort_keys=True, indent=4, default=str)
###############################################################################


if __name__ == '__main__':
    main()
