import json
import azure.functions as func
from shared.db import get_ads_collection
from bson import ObjectId

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get("id")
        if not id:
            return func.HttpResponse("Missing id", status_code=400)

        body = req.get_json()
        collection = get_ads_collection()

        result = collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return func.HttpResponse("Not found", status_code=404)

        return func.HttpResponse(
            json.dumps({"id": id, "status": "updated"}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)
