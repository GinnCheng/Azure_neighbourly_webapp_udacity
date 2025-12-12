from shared.db import get_ads_collection
import json
import azure.functions as func
import pymongo
import os
from bson import ObjectId

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')

        if not id:
            return func.HttpResponse("Missing id", status_code=400)

        collection = get_ads_collection()

        result = collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            return func.HttpResponse("Not found", status_code=404)

        return func.HttpResponse("Deleted", status_code=200)

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)
