import json
import azure.functions as func
from ...shared.db import get_ads_collection

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
    except:
        return func.HttpResponse("Invalid JSON", status_code=400)

    try:
        collection = get_ads_collection()
        result = collection.insert_one(data)
        data["_id"] = str(result.inserted_id)

        return func.HttpResponse(
            json.dumps(data),
            mimetype="application/json",
            status_code=201
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)
