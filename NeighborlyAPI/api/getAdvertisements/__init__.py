import json
import azure.functions as func
from ...shared.db import get_ads_collection

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        collection = get_ads_collection()
        ads = []

        for doc in collection.find():
            doc["_id"] = str(doc["_id"])
            ads.append(doc)

        return func.HttpResponse(
            json.dumps(ads),
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error: {e}",
            status_code=500
        )
