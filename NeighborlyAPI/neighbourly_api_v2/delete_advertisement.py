from azure.functions.decorators import HttpTrigger, HttpOutput
from . import app
from shared.db import get_ads_collection

@app.function_name(name="deleteAdvertisement")
@app.route(route="deleteadvertisement/{id}", methods=["DELETE"], auth_level="ANONYMOUS")
def delete_ad(req: HttpTrigger, id: str) -> HttpOutput:
    try:
        collection = get_ads_collection()
        result = collection.delete_one({"_id": id})

        if result.deleted_count == 0:
            return HttpOutput("Not found", status_code=404)

        return HttpOutput("Deleted", status_code=200)

    except Exception as e:
        return HttpOutput(str(e), status_code=500)
