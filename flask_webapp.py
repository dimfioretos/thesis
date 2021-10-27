#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import json
import pprint
import time
import logging
from logging.config import dictConfig

import twitter_library as tlb
import with_preloaded_model as classifier

from flask import Flask, render_template, request, send_file
from flask_httpauth import HTTPBasicAuth
import networkx as nx
import matplotlib.pyplot as plt

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
logging.basicConfig(filename='app.log',level=logging.DEBUG)

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == '1' and password == '2':
            return True
        else:
            return False
    return False
###############################################################################


@app.route("/", methods=['GET'])
@auth.login_required()
def get_index():
    return render_template("index.html")
###############################################################################


@app.route("/results", methods=['post', 'get'])
@app.route("/results_json", methods=['get'])
@app.route("/results_graph", methods=['get'])
@app.route("/results_image", methods=['get'])
@auth.login_required()
def post_results():
    start = time.time()

    query = request.form.get('query', None)
    date_from = request.form.get('date_from', None)
    date_until = request.form.get('date_until', None)
    min_retweets = request.form.get('min_retweets', None)
    min_replies = request.form.get('min_replies', None)
    min_likes = request.form.get('min_likes', None)
    limit = request.form.get('limit', 20)
    username = request.form.get('username', None)

    if not date_from:
        date_from = None
    if not date_until:
        date_until = None
    if not min_retweets and min_retweets not in ['0', 0]:
        min_retweets = None
    if not min_replies and min_replies not in ['0', 0]:
        min_replies = None
    if not min_likes and min_likes not in ['0', 0]:
        min_likes = None
    if not limit:
        limit = 20
    if not username:
        username = None

    if request.method in ['post', 'POST']:
        app.logger.info("Received POST request with form data: "
                        "query: %s , date_from: %s , date_until: %s , "
                        "min_retweets: %s , min_replies: %s , min_likes: %s , "
                        "limit: %s , username: %s", query, date_from,
                        date_until, min_retweets, min_replies, min_likes,
                        limit, username)

        if query:
            data = dict()
            search_results = tlb.search(query, date_from, date_until, min_retweets,
                                        min_replies, min_likes, limit, username)
            t2 = time.time()

            for idx, tweet in enumerate(search_results):
                t1 = time.time()
                app.logger.info("Fetching replies for tweet %s out of %s",
                                idx+1, len(search_results))
                replies = tlb.get_replies(tweet)
                t2 = time.time()
                data[tweet.id] = {
                    'original_tweet': tweet,
                    'replies': replies
                }

        graph_data = {'nodes': [], 'edges': []}
        nodes = dict()
        for idx, key in enumerate(data):
            if data[key]['original_tweet'].username not in nodes:
                app.logger.info("Classifying %s out of %s tweets: %s", idx+1,
                                len(data), data[key]['original_tweet'].tweet)

                classification = classifier.classify(
                    data[key]['original_tweet'].tweet)
                if classification == 'fake':
                    role = 'fake'
                else:
                    role = 'not_fake'

                nodes[str(data[key]['original_tweet'].id)] = {
                    "id": str(data[key]['original_tweet'].id),
                    "caption": data[key]['original_tweet'].username,
                    "role": role,
                    "link": data[key]['original_tweet'].link,
                    "text": data[key]['original_tweet'].tweet,
                    "interactions": data[key]['original_tweet'].likes_count \
                                  + data[key]['original_tweet'].replies_count \
                                  + data[key]['original_tweet'].retweets_count
                }
            for idx2, reply in enumerate(data[key]['replies']):
                if reply.username not in nodes:
                    app.logger.info("Classifying %s out of %s replies for tweet %s: %s",
                                    idx2+1, len(data[key]['replies']),
                                    idx+1, reply.tweet)

                    classification = classifier.classify(reply.tweet)
                    if classification == 'fake':
                        role = 'fake'
                    else:
                        role = 'not_fake'

                    nodes[str(reply.id)] = {
                        "id": str(reply.id),
                        "caption": reply.username,
                        "role": role,
                        "link": reply.link,
                        "text": reply.tweet,
                        "interactions": reply.likes_count \
                                      + reply.replies_count \
                                      + reply.retweets_count
                    }

                edge = {
                    "source": str(data[key]['original_tweet'].id),
                    "target": str(reply.id)
                }
                if edge not in graph_data['edges'] and edge['source'] != edge['target']:
                    graph_data['edges'].append(edge)
            graph_data['nodes'] = list(nodes.values())
            node_types = {
                "role":  ["fake", "not_fake"]
            }

        if graph_data['nodes']:
            largest_radius = max([x['interactions'] for x in graph_data['nodes']])

        app.logger.info("Rendering graph: %s"  %(json.dumps(graph_data)))
        app.logger.info("Request completed after %.2lf seconds" % (time.time() - start))

        if 'json' in request.path or request.form.get("return_type") == 'json':
            return graph_data
        elif request.form.get("return_type") == 'graph' or request.method in ['get', 'GET']:
            if len(data) == 0:
                return render_template("empty_results.html")
            else:
                return render_template("results.html", data=json.dumps(graph_data),
                                       node_types=node_types, extra_data=nodes,
                                       largest_radius=largest_radius)
        elif request.form.get("return_type") == 'image':
            return send_file(plot_image(graph_data), mimetype='image/PNG')
        else:
            return "Bad Request", 401
    else:  # request is of type GET, return sample data
        with open('sample_graph_data.json') as infile:
            graph_data = json.load(infile)
        with open('sample_extra_data.json') as infile:
            nodes = json.load(infile)
        largest_radius = max([x['interactions'] for x in graph_data['nodes']])
        node_types = { "role":  ["fake", "not_fake"] }

        if 'json' in request.path:
            return graph_data
        elif 'graph' in request.path:
            return render_template("results.html", data=json.dumps(graph_data),
                                   node_types=node_types, extra_data=nodes,
                                   largest_radius=largest_radius)
        elif 'image' in request.path:
            return send_file(plot_image(graph_data), mimetype='image/PNG')
        else:
            return "Bad Request", 401
###############################################################################


def plot_image(graph_data):
    """Plot a static PNG image of the given graph data"""
    tmpFile = io.BytesIO()

    graph = nx.Graph()
    for item in graph_data['nodes']:
        color = 'green'
        if item['role'] == 'fake':
            color = 'red'
        graph.add_node(item['id'], color=color)
    for item in graph_data['edges']:
        graph.add_edge(item["source"], item["target"])
    colors = [node[1]['color'] for node in graph.nodes(data=True)]

    plt.savefig(tmpFile, format='png')
    nx.draw(graph, node_color=colors)
    plt.savefig(tmpFile, format='png')
    tmpFile.seek(0)
    return tmpFile
###############################################################################


if __name__ == "__main__":
    app.run(debug=True)
