import json
from azure.functions.decorators import HttpTrigger, HttpOutput
from . import app
from shared.db import get_ads_collection

@app.function_name(name="createAdvertisement")
@app.route(route="createadvertisement", methods=["POST"], auth_level="ANONYMOUS")
def create_ad(req: HttpTrigger) -> HttpOutput:
    try:
        data = req.get_json()
        collection = get_ads_collection()

        result = collection.insert_one(data)
        data["_id"] = str(result.inserted_id)

        return HttpOutput(
            json.dumps(data),
            status_code=201,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return HttpOutput(str(e), status_code=500)
