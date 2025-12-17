# getPost/__init__.py

import json
import azure.functions as func
from shared.db import get_posts_collection

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        post_id = req.route_params.get("id")
        if not post_id:
            return func.HttpResponse("Missing id", status_code=400)

        collection = get_posts_collection()

        doc = collection.find_one({"id": post_id})

        if not doc:
            return func.HttpResponse("Not found", status_code=404)

        return func.HttpResponse(
            json.dumps(doc),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)