import json
import azure.functions as func
from shared.db import get_posts_collection

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        collection = get_posts_collection()
        posts = []

        for doc in collection.find():
            posts.append(doc)

        return func.HttpResponse(
            json.dumps(posts),
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error: {e}",
            status_code=500
        )