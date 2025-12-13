import os
from pymongo import MongoClient

def _get_client():
    url = os.environ["MyDbConnection"]
    return MongoClient(
        url,
        tls=True,
        tlsAllowInvalidCertificates=True
    )

def get_ads_collection():
    client = _get_client()
    db = client["neighbourlydb"]
    return db["advertisements"]

def get_posts_collection():
    client = _get_client()
    db = client["neighbourlydb"]
    return db["posts"]
