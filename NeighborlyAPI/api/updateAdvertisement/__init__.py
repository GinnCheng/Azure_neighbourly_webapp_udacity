import json
import azure.functions as func
from ...shared.db import get_ads_collection
from bson.objectid import ObjectId

def main(req: func.HttpRequest) -> func.HttpResponse:
    ad_id = req.params.get("id")
    if not ad_id:
        return func.HttpResponse("Missing id", status_code=400)

    try:
        new_data = req.get_json()
    except:
        return func.HttpResponse("Invalid JSON", status_code=400)

    try:
        collection = get_ads_collection()
        result = collection.update_one(
            {"_id": ObjectId(ad_id)},
            {"$set": new_data}
        )

        if result.matched_count == 0:
            return func.HttpResponse("Not found", status_code=404)

        new_data["_id"] = ad_id
        return func.HttpResponse(json.dumps(new_data), mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)
