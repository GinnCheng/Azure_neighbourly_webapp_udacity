import os
import pymongo

def get_ads_collection():
    client = pymongo.MongoClient(os.environ["MyDbConnection"])
    db = client["neighbourlydb"]
    return db["advertisements"]

def get_posts_collection():
    client = pymongo.MongoClient(os.environ["MyDbConnection"])
    db = client["neighbourlydb"]
    return db["posts"]
