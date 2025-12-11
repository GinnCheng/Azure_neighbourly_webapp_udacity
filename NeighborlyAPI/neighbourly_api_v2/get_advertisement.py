import json
from azure.functions.decorators import HttpTrigger, HttpOutput
from . import app
from shared.db import get_ads_collection

@app.function_name(name="getAdvertisement")
@app.route(route="getadvertisement/{id}", methods=["GET"], auth_level="ANONYMOUS")
def get_ad(req: HttpTrigger, id: str) -> HttpOutput:
    try:
        collection = get_ads_collection()
        ad = collection.find_one({"_id": id})

        if not ad:
            return HttpOutput("Not found", status_code=404)

        ad["_id"] = str(ad["_id"])
        return HttpOutput(
            json.dumps(ad),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        return HttpOutput(str(e), status_code=500)
