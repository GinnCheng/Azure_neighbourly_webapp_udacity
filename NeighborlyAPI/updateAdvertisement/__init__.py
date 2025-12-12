import json
import azure.functions as func
from shared.db import get_ads_collection
from bson import ObjectId

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        ad_id = req.route_params.get("id")
        if not ad_id:
            return func.HttpResponse("Missing id", status_code=400)

        req_body = req.get_json()
        collection = get_ads_collection()

        result = collection.update_one(
            {"_id": ObjectId(ad_id)},
            {"$set": body}
        )


        if result.matched_count == 0:
            return func.HttpResponse("No item found", status_code=404)

        return func.HttpResponse("Successfully updated", status_code=200)

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
