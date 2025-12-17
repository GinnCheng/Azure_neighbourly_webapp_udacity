import json
import azure.functions as func
from shared.db import get_posts_collection
from bson import ObjectId

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        post_id = req.route_params.get("id")
        if not post_id:
            return func.HttpResponse("Missing id", status_code=400)

        collection = get_posts_collection()

        # ✅ 用 MongoDB _id 查询
        try:
            doc = collection.find_one({"_id": ObjectId(post_id)})
        except Exception:
            return func.HttpResponse("Invalid id format", status_code=400)

        if not doc:
            return func.HttpResponse("Not found", status_code=404)

        # ✅ ObjectId → string
        doc["_id"] = str(doc["_id"])

        return func.HttpResponse(
            json.dumps(doc),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)