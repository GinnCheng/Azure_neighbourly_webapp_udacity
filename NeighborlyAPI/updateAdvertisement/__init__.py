import json
import azure.functions as func
from shared.db import get_ads_collection
from bson.objectid import ObjectId
from bson.errors import InvalidId


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        ad_id = req.route_params.get("id")
        if not ad_id:
            return func.HttpResponse("Missing id", status_code=400)

        try:
            obj_id = ObjectId(ad_id)
        except InvalidId:
            return func.HttpResponse("Invalid id format", status_code=400)

        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse("Empty request body", status_code=400)

        collection = get_ads_collection()

        result = collection.update_one(
            {"_id": obj_id},
            {"$set": req_body}
        )

        if result.matched_count == 0:
            return func.HttpResponse("No item found", status_code=404)

        return func.HttpResponse(
            json.dumps({"message": "Successfully updated"}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
