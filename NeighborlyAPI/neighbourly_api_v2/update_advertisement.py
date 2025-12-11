from azure.functions.decorators import HttpTrigger, HttpOutput
from . import app
from ..neighbourly_api_v2.shared.db import get_ads_collection

@app.function_name(name="updateAdvertisement")
@app.route(route="updateadvertisement/{id}", methods=["PUT"], auth_level="ANONYMOUS")
def update_ad(req: HttpTrigger, id: str) -> HttpOutput:
    try:
        body = req.get_json()
        collection = get_ads_collection()

        result = collection.update_one({"_id": id}, {"$set": body})

        if result.modified_count == 0:
            return HttpOutput("Not found or no change", status_code=404)

        return HttpOutput("Updated", status_code=200)

    except Exception as e:
        return HttpOutput(str(e), status_code=500)
