import json
import azure.functions as func
from ...shared.db import get_ads_collection
from bson.objectid import ObjectId

def main(req: func.HttpRequest) -> func.HttpResponse:
    ad_id = req.params.get("id")
    if not ad_id:
        return func.HttpResponse("Missing id", status_code=400)

    try:
        collection = get_ads_collection()
        doc = collection.find_one({"_id": ObjectId(ad_id)})

        if not doc:
            return func.HttpResponse("Not found", status_code=404)

        doc["_id"] = str(doc["_id"])
        return func.HttpResponse(json.dumps(doc), mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)
