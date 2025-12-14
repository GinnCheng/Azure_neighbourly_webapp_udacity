import json
import azure.functions as func
from shared.db import get_ads_collection

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        raw_body = req.get_body()
        if not raw_body:
            return func.HttpResponse("Empty request body", status_code=400)

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception:
            return func.HttpResponse("Invalid JSON", status_code=400)

        if not isinstance(data, dict):
            return func.HttpResponse("JSON must be an object", status_code=400)

        collection = get_ads_collection()
        result = collection.insert_one(data)

        data["_id"] = str(result.inserted_id)

        return func.HttpResponse(
            json.dumps(data),
            status_code=201,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
