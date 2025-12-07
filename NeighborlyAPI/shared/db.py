import os
import pymongo

def get_ads_collection():
    url = os.environ["MyDbConnection"]
    client = pymongo.MongoClient(url)
    database = client["neighborly"]
    return database["advertisements"]

def get_posts_collection():
    url = os.environ["MyDbConnection"]
    client = pymongo.MongoClient(url)
    database = client["neighborly"]
    return database["posts"]
