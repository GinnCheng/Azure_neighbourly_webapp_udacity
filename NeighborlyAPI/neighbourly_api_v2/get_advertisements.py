import json
from azure.functions.decorators import HttpTrigger, HttpOutput
from . import app
from shared.db import get_ads_collection

@app.function_name(name="getAdvertisements")
@app.route(route="getadvertisements", methods=["GET"], auth_level="ANONYMOUS")
def get_ads(req: HttpTrigger) -> HttpOutput:
    try:
        collection = get_ads_collection()
        ads = list(collection.find())

        for ad in ads:
            ad["_id"] = str(ad["_id"])

        return HttpOutput(
            json.dumps(ads),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return HttpOutput(str(e), status_code=500)
