import azure.functions as func
from shared.db import get_ads_collection
import pymongo
import os
import json

def main(req: func.HttpRequest, id: str) -> func.HttpResponse:
    try:
        if not id:
            return func.HttpResponse("Missing id", status_code=400)

        req_body = req.get_json()
        collection = get_ads_collection()

        update = { "$set": req_body }
        result = collection.update_one({"_id": id}, update)

        if result.matched_count == 0:
            return func.HttpResponse("No item found", status_code=404)

        return func.HttpResponse("Successfully updated", status_code=200)

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
